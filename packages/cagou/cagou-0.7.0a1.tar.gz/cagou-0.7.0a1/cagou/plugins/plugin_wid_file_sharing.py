#!/usr/bin/python
# -*- coding: utf-8 -*-

# Cagou: desktop/mobile frontend for Salut à Toi XMPP client
# Copyright (C) 2016-2018 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from sat.core import log as logging
from sat.core import exceptions
log = logging.getLogger(__name__)
from sat.core.i18n import _
from sat.tools.common import files_utils
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.tools import jid
from cagou.core.constants import Const as C
from cagou.core import cagou_widget
from cagou.core.menu import (EntitiesSelectorMenu, TouchMenuBehaviour,
                             TouchMenuItemBehaviour)
from cagou.core.utils import FilterBehavior
from cagou import G
from kivy import properties
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy import utils as kivy_utils
from functools import partial
import os.path
import json


PLUGIN_INFO = {
    "name": _(u"file sharing"),
    "main": "FileSharing",
    "description": _(u"share/transfer files between devices"),
    "icon_symbol": u"exchange",
}
MODE_VIEW = u"view"
MODE_LOCAL = u"local"
SELECT_INSTRUCTIONS = _(u"Please select entities to share with")

if kivy_utils.platform == "android":
    from jnius import autoclass
    Environment = autoclass("android.os.Environment")
    base_dir = Environment.getExternalStorageDirectory().getAbsolutePath()
    def expanduser(path):
        if path == u'~' or path.startswith(u'~/'):
            return path.replace(u'~', base_dir, 1)
        return path
else:
    expanduser = os.path.expanduser


class ModeBtn(Button):

    def __init__(self, parent, **kwargs):
        super(ModeBtn, self).__init__(**kwargs)
        parent.bind(mode=self.on_mode)
        self.on_mode(parent, parent.mode)

    def on_mode(self, parent, new_mode):
        if new_mode == MODE_VIEW:
            self.text = _(u"view shared files")
        elif new_mode == MODE_LOCAL:
            self.text = _(u"share local files")
        else:
            exceptions.InternalError(u"Unknown mode: {mode}".format(mode=new_mode))


class Identities(object):

    def __init__(self, entity_ids):
        identities = {}
        for cat, type_, name in entity_ids:
            identities.setdefault(cat, {}).setdefault(type_, []).append(name)
        client = identities.get('client', {})
        if 'pc' in client:
            self.type = 'desktop'
        elif 'phone' in client:
            self.type = 'phone'
        elif 'web' in client:
            self.type = 'web'
        elif 'console' in client:
            self.type = 'console'
        else:
            self.type = 'desktop'

        self.identities = identities

    @property
    def name(self):
        return self.identities.values()[0].values()[0][0]


class ItemWidget(TouchMenuItemBehaviour, BoxLayout):
    name = properties.StringProperty()
    base_width = properties.NumericProperty(dp(100))


class PathWidget(ItemWidget):

    def __init__(self, filepath, main_wid, **kw):
        name = os.path.basename(filepath)
        self.filepath = os.path.normpath(filepath)
        if self.filepath == u'.':
            self.filepath = u''
        super(PathWidget, self).__init__(name=name, main_wid=main_wid, **kw)

    @property
    def is_dir(self):
        raise NotImplementedError

    def do_item_action(self, touch):
        if self.is_dir:
            self.main_wid.current_dir = self.filepath

    def open_menu(self, touch, dt):
        log.debug(_(u"opening menu for {path}").format(path=self.filepath))
        super(PathWidget, self).open_menu(touch, dt)


class LocalPathWidget(PathWidget):

    @property
    def is_dir(self):
        return os.path.isdir(self.filepath)

    def getMenuChoices(self):
        choices = []
        if self.shared:
            choices.append(dict(text=_(u'unshare'),
                                index=len(choices)+1,
                                callback=self.main_wid.unshare))
        else:
            choices.append(dict(text=_(u'share'),
                                index=len(choices)+1,
                                callback=self.main_wid.share))
        return choices


class RemotePathWidget(PathWidget):

    def __init__(self, main_wid, filepath, type_, **kw):
        self.type_ = type_
        super(RemotePathWidget, self).__init__(filepath, main_wid=main_wid, **kw)

    @property
    def is_dir(self):
        return self.type_ == C.FILE_TYPE_DIRECTORY

    def do_item_action(self, touch):
        if self.is_dir:
            if self.filepath == u'..':
                self.main_wid.remote_entity = u''
            else:
                super(RemotePathWidget, self).do_item_action(touch)
        else:
            self.main_wid.request_item(self)
            return True


class DeviceWidget(ItemWidget):

    def __init__(self, main_wid, entity_jid, identities, **kw):
        self.entity_jid = entity_jid
        self.identities = identities
        own_jid = next(G.host.profiles.itervalues()).whoami
        self.own_device = entity_jid.bare == own_jid
        if self.own_device:
            name = self.identities.name
        elif self.entity_jid.node:
            name = self.entity_jid.node
        elif self.entity_jid.domain.endswith(own_jid.domain):
            name = _(u"your server")
        else:
            name = _(u"sharing component")

        super(DeviceWidget, self).__init__(name=name, main_wid=main_wid, **kw)

    def getSymbol(self):
        if self.identities.type == 'desktop':
            return 'desktop'
        elif self.identities.type == 'phone':
            return 'mobile'
        elif self.identities.type == 'web':
            return 'globe'
        elif self.identities.type == 'console':
            return 'terminal'
        else:
            return 'desktop'

    def do_item_action(self, touch):
        self.main_wid.remote_entity = self.entity_jid
        self.main_wid.remote_dir = u''


class CategorySeparator(Label):
    pass


class FileSharing(quick_widgets.QuickWidget, cagou_widget.CagouWidget, FilterBehavior,
                  TouchMenuBehaviour):
    SINGLE=False
    layout = properties.ObjectProperty()
    mode = properties.OptionProperty(MODE_LOCAL, options=[MODE_VIEW, MODE_LOCAL])
    local_dir = properties.StringProperty(expanduser(u'~'))
    remote_dir = properties.StringProperty(u'')
    remote_entity = properties.StringProperty(u'')
    shared_paths = properties.ListProperty()
    signals_registered = False

    def __init__(self, host, target, profiles):
        quick_widgets.QuickWidget.__init__(self, host, target, profiles)
        cagou_widget.CagouWidget.__init__(self)
        FilterBehavior.__init__(self)
        TouchMenuBehaviour.__init__(self)
        self.mode_btn = ModeBtn(self)
        self.mode_btn.bind(on_release=self.change_mode)
        self.headerInputAddExtra(self.mode_btn)
        self.bind(local_dir=self.update_view,
                  remote_dir=self.update_view,
                  remote_entity=self.update_view)
        self.update_view()
        if not FileSharing.signals_registered:
            # FIXME: we use this hack (registering the signal for the whole class) now
            #        as there is currently no unregisterSignal available in bridges
            G.host.registerSignal("FISSharedPathNew",
                                  handler=FileSharing.shared_path_new,
                                  iface="plugin")
            G.host.registerSignal("FISSharedPathRemoved",
                                  handler=FileSharing.shared_path_removed,
                                  iface="plugin")
            FileSharing.signals_registered = True
        G.host.bridge.FISLocalSharesGet(self.profile,
                                        callback=self.fill_paths,
                                        errback=G.host.errback)

    @property
    def current_dir(self):
        return self.local_dir if self.mode == MODE_LOCAL else self.remote_dir

    @current_dir.setter
    def current_dir(self, new_dir):
        if self.mode == MODE_LOCAL:
            self.local_dir = new_dir
        else:
            self.remote_dir = new_dir

    def fill_paths(self, shared_paths):
        self.shared_paths.extend(shared_paths)

    def change_mode(self, mode_btn):
        self.clear_menu()
        opt = self.__class__.mode.options
        new_idx = (opt.index(self.mode)+1) % len(opt)
        self.mode = opt[new_idx]

    def on_mode(self, instance, new_mode):
        self.update_view(None, self.local_dir)

    def onHeaderInput(self):
        if u'/' in self.header_input.text or self.header_input.text == u'~':
            self.current_dir = expanduser(self.header_input.text)

    def onHeaderInputComplete(self, wid, text, **kwargs):
        """we filter items when text is entered in input box"""
        if u'/' in text:
            return
        self.do_filter(self.layout.children,
                       text,
                       lambda c: c.name,
                       width_cb=lambda c: c.base_width,
                       height_cb=lambda c: c.minimum_height,
                       continue_tests=[lambda c: not isinstance(c, ItemWidget),
                                       lambda c: c.name == u'..'])


    ## remote sharing callback ##

    def _discoFindByFeaturesCb(self, data):
        entities_services, entities_own, entities_roster = data
        for entities_map, title in ((entities_services,
                                     _(u'services')),
                                    (entities_own,
                                     _(u'your devices')),
                                    (entities_roster,
                                     _(u'your contacts devices'))):
            if entities_map:
                self.layout.add_widget(CategorySeparator(text=title))
                for entity_str, entity_ids in entities_map.iteritems():
                    entity_jid = jid.JID(entity_str)
                    item = DeviceWidget(self,
                                        entity_jid,
                                        Identities(entity_ids))
                    self.layout.add_widget(item)
        if not entities_services and not entities_own and not entities_roster:
            self.layout.add_widget(Label(
                size_hint=(1, 1),
                halign='center',
                text_size=self.size,
                text=_(u"No sharing device found")))

    def discover_devices(self):
        """Looks for devices handling file "File Information Sharing" and display them"""
        try:
            namespace = self.host.ns_map['fis']
        except KeyError:
            msg = _(u"can't find file information sharing namespace, "
                    u"is the plugin running?")
            log.warning(msg)
            G.host.addNote(_(u"missing plugin"), msg, C.XMLUI_DATA_LVL_ERROR)
            return
        self.host.bridge.discoFindByFeatures(
            [namespace], [], False, True, True, True, False, self.profile,
            callback=self._discoFindByFeaturesCb,
            errback=partial(G.host.errback,
                title=_(u"shared folder error"),
                message=_(u"can't check sharing devices: {msg}")))

    def FISListCb(self, files_data):
        for file_data in files_data:
            filepath = os.path.join(self.current_dir, file_data[u'name'])
            item = RemotePathWidget(
                filepath=filepath,
                main_wid=self,
                type_=file_data[u'type'])
            self.layout.add_widget(item)

    def FISListEb(self, failure_):
        self.remote_dir = u''
        G.host.addNote(
            _(u"shared folder error"),
            _(u"can't list files for {remote_entity}: {msg}").format(
                remote_entity=self.remote_entity,
                msg=failure_),
            level=C.XMLUI_DATA_LVL_WARNING)

    ## view generation ##

    def update_view(self, *args):
        """update items according to current mode, entity and dir"""
        log.debug(u'updating {}, {}'.format(self.current_dir, args))
        self.layout.clear_widgets()
        self.header_input.text = u''
        self.header_input.hint_text = self.current_dir

        if self.mode == MODE_LOCAL:
            filepath = os.path.join(self.local_dir, u'..')
            self.layout.add_widget(LocalPathWidget(filepath=filepath, main_wid=self))
            try:
                files = sorted(os.listdir(self.local_dir))
            except OSError as e:
                msg = _(u"can't list files in \"{local_dir}\": {msg}").format(
                    local_dir=self.local_dir,
                    msg=e)
                G.host.addNote(
                    _(u"shared folder error"),
                    msg,
                    level=C.XMLUI_DATA_LVL_WARNING)
                self.local_dir = expanduser(u'~')
                return
            for f in files:
                filepath = os.path.join(self.local_dir, f)
                self.layout.add_widget(LocalPathWidget(filepath=filepath,
                                                       main_wid=self))
        elif self.mode == MODE_VIEW:
            if not self.remote_entity:
                self.discover_devices()
            else:
                # we always a way to go back
                # so user can return to previous list even in case of error
                parent_path = os.path.join(self.remote_dir, u'..')
                item = RemotePathWidget(
                    filepath = parent_path,
                    main_wid=self,
                    type_ = C.FILE_TYPE_DIRECTORY)
                self.layout.add_widget(item)
                self.host.bridge.FISList(
                    unicode(self.remote_entity),
                    self.remote_dir,
                    {},
                    self.profile,
                    callback=self.FISListCb,
                    errback=self.FISListEb)

    ## Share methods ##

    def do_share(self, entities_jids, item):
        if entities_jids:
            access = {u'read': {u'type': 'whitelist',
                                u'jids': entities_jids}}
        else:
            access = {}

        G.host.bridge.FISSharePath(
            item.name,
            item.filepath,
            json.dumps(access, ensure_ascii=False),
            self.profile,
            callback=lambda name: G.host.addNote(
                _(u"sharing folder"),
                _(u"{name} is now shared").format(name=name)),
            errback=partial(G.host.errback,
                title=_(u"sharing folder"),
                message=_(u"can't share folder: {msg}")))

    def share(self, menu):
        item = self.menu_item
        self.clear_menu()
        EntitiesSelectorMenu(instructions=SELECT_INSTRUCTIONS,
                             callback=partial(self.do_share, item=item)).show()

    def unshare(self, menu):
        item = self.menu_item
        self.clear_menu()
        G.host.bridge.FISUnsharePath(
            item.filepath,
            self.profile,
            callback=lambda: G.host.addNote(
                _(u"sharing folder"),
                _(u"{name} is not shared anymore").format(name=item.name)),
            errback=partial(G.host.errback,
                title=_(u"sharing folder"),
                message=_(u"can't unshare folder: {msg}")))

    def fileJingleRequestCb(self, progress_id, item, dest_path):
        G.host.addNote(
            _(u"file request"),
            _(u"{name} download started at {dest_path}").format(
                name = item.name,
                dest_path = dest_path))

    def request_item(self, item):
        """Retrieve an item from remote entity

        @param item(RemotePathWidget): item to retrieve
        """
        path, name = os.path.split(item.filepath)
        assert name
        assert self.remote_entity
        extra = {'path': path}
        dest_path = files_utils.get_unique_name(os.path.join(G.host.downloads_dir, name))
        G.host.bridge.fileJingleRequest(unicode(self.remote_entity),
                                        dest_path,
                                        name,
                                        u'',
                                        u'',
                                        extra,
                                        self.profile,
                                        callback=partial(self.fileJingleRequestCb,
                                            item=item,
                                            dest_path=dest_path),
                                        errback=partial(G.host.errback,
                                            title = _(u"file request error"),
                                            message = _(u"can't request file: {msg}")))

    @classmethod
    def shared_path_new(cls, shared_path, name, profile):
        for wid in G.host.getVisibleList(cls):
            if shared_path not in wid.shared_paths:
                wid.shared_paths.append(shared_path)

    @classmethod
    def shared_path_removed(cls, shared_path, profile):
        for wid in G.host.getVisibleList(cls):
            if shared_path in wid.shared_paths:
                wid.shared_paths.remove(shared_path)
            else:
                log.warning(_(u"shared path {path} not found in {widget}".format(
                    path = shared_path, widget = wid)))

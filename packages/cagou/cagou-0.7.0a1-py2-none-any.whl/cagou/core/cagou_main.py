#!/usr//bin/env python2
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


from sat.core.i18n import _
from . import kivy_hack
kivy_hack.do_hack()
from constants import Const as C
from sat.core import log as logging
log = logging.getLogger(__name__)
from sat.core import exceptions
from sat_frontends.quick_frontend.quick_app import QuickApp
from sat_frontends.quick_frontend import quick_widgets
from sat_frontends.quick_frontend import quick_chat
from sat_frontends.quick_frontend import quick_utils
from sat.tools import config
from sat.tools.common import dynamic_import
import kivy
kivy.require('1.10.0')
import kivy.support
main_config = config.parseMainConf()
bridge_name = config.getConfig(main_config, '', 'bridge', 'dbus')
# FIXME: event loop is choosen according to bridge_name, a better way should be used
if 'dbus' in bridge_name:
    kivy.support.install_gobject_iteration()
elif bridge_name in ('pb', 'embedded'):
    kivy.support.install_twisted_reactor()
from kivy.app import App
from kivy.lang import Builder
from kivy import properties
import xmlui
from profile_manager import ProfileManager
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import (ScreenManager, Screen,
                                    FallOutTransition, RiseInTransition)
from kivy.uix.dropdown import DropDown
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.metrics import dp
from cagou_widget import CagouWidget
from . import widgets_handler
from .common import IconButton
from . import menu
from . import dialog
from importlib import import_module
import os.path
import glob
import cagou.plugins
import cagou.kv
from kivy import utils as kivy_utils
import sys
try:
    from plyer import notification
except ImportError:
    notification = None
    log.warning(_(u"Can't import plyer, some features disabled"))

# we want white background by default
Window.clearcolor = (1, 1, 1, 1)


if kivy_utils.platform == "android":
    # FIXME: move to separate android module
    # sys.platform is "linux" on android by default
    # so we change it to allow backend to detect android
    sys.platform = "android"
    import mmap
    C.PLUGIN_EXT = 'pyo'


class NotifsIcon(IconButton):
    notifs = properties.ListProperty()

    def on_release(self):
        callback, args, kwargs = self.notifs.pop(0)
        callback(*args, **kwargs)

    def addNotif(self, callback, *args, **kwargs):
        self.notifs.append((callback, args, kwargs))


class Note(Label):
    title = properties.StringProperty()
    message = properties.StringProperty()
    level = properties.OptionProperty(C.XMLUI_DATA_LVL_DEFAULT,
                                      options=list(C.XMLUI_DATA_LVLS))


class NoteDrop(Label):
    title = properties.StringProperty()
    message = properties.StringProperty()
    level = properties.OptionProperty(C.XMLUI_DATA_LVL_DEFAULT,
                                      options=list(C.XMLUI_DATA_LVLS))


class NotesDrop(DropDown):
    clear_btn = properties.ObjectProperty()

    def __init__(self, notes):
        super(NotesDrop, self).__init__()
        self.notes = notes

    def open(self, widget):
        self.clear_widgets()
        for n in self.notes:
            self.add_widget(NoteDrop(title=n.title, message=n.message, level=n.level))
        self.add_widget(self.clear_btn)
        super(NotesDrop, self).open(widget)


class RootHeadWidget(BoxLayout):
    """Notifications widget"""
    manager = properties.ObjectProperty()
    notifs_icon = properties.ObjectProperty()
    notes = properties.ListProperty()
    HEIGHT = dp(35)

    def __init__(self):
        super(RootHeadWidget, self).__init__()
        self.notes_last = None
        self.notes_event = None
        self.notes_drop = NotesDrop(self.notes)

    def addNotif(self, callback, *args, **kwargs):
        """add a notification with a callback attached

        when notification is pressed, callback is called
        @param *args, **kwargs: arguments of callback
        """
        self.notifs_icon.addNotif(callback, *args, **kwargs)

    def addNote(self, title, message, level):
        note = Note(title=title, message=message, level=level)
        self.notes.append(note)
        if self.notes_event is None:
            self.notes_event = Clock.schedule_interval(self._displayNextNote, 5)
            self._displayNextNote()

    def addNotifUI(self, ui):
        self.notifs_icon.addNotif(ui.show, force=True)

    def addNotifWidget(self, widget):
        app = App.get_running_app()
        self.notifs_icon.addNotif(app.host.showExtraUI, widget=widget)

    def _displayNextNote(self, dummy=None):
        screen = Screen()
        try:
            idx = self.notes.index(self.notes_last) + 1
        except ValueError:
            idx = 0
        try:
            note = self.notes_last = self.notes[idx]
        except IndexError:
            self.notes_event.cancel()
            self.notes_event = None
        else:
            screen.add_widget(note)
        self.manager.switch_to(screen)


class RootMenus(menu.MenusWidget):
    HEIGHT = dp(30)


class RootBody(BoxLayout):
    pass


class CagouRootWidget(FloatLayout):
    root_menus = properties.ObjectProperty()
    root_body = properties.ObjectProperty

    def __init__(self, main_widget):
        super(CagouRootWidget, self).__init__()
        # header
        self.head_widget = RootHeadWidget()
        self.root_body.add_widget(self.head_widget)
        # body
        self._manager = ScreenManager()
        # main widgets
        main_screen = Screen(name='main')
        main_screen.add_widget(main_widget)
        self._manager.add_widget(main_screen)
        # backend XMLUI (popups, forms, etc)
        xmlui_screen = Screen(name='xmlui')
        self._manager.add_widget(xmlui_screen)
        # extra (file chooser, audio record, etc)
        extra_screen = Screen(name='extra')
        self._manager.add_widget(extra_screen)
        self.root_body.add_widget(self._manager)

    def changeWidget(self, widget, screen_name="main"):
        """change main widget"""
        if self._manager.transition.is_active:
            # FIXME: workaround for what seems a Kivy bug
            # TODO: report this upstream
            self._manager.transition.stop()
        screen = self._manager.get_screen(screen_name)
        screen.clear_widgets()
        screen.add_widget(widget)

    def show(self, screen="main"):
        if self._manager.transition.is_active:
            # FIXME: workaround for what seems a Kivy bug
            # TODO: report this upstream
            self._manager.transition.stop()
        if self._manager.current == screen:
            return
        if screen == "main":
            self._manager.transition = FallOutTransition()
        else:
            self._manager.transition = RiseInTransition()
        self._manager.current = screen

    def newAction(self, handler, action_data, id_, security_limit, profile):
        """Add a notification for an action"""
        self.head_widget.addNotif(handler, action_data, id_, security_limit, profile)

    def addNote(self, title, message, level):
        self.head_widget.addNote(title, message, level)

    def addNotifUI(self, ui):
        self.head_widget.addNotifUI(ui)

    def addNotifWidget(self, widget):
        self.head_widget.addNotifWidget(widget)


class CagouApp(App):
    """Kivy App for Cagou"""
    c_prim = properties.ListProperty(C.COLOR_PRIM)
    c_prim_light = properties.ListProperty(C.COLOR_PRIM_LIGHT)
    c_prim_dark = properties.ListProperty(C.COLOR_PRIM_DARK)
    c_sec = properties.ListProperty(C.COLOR_SEC)
    c_sec_light = properties.ListProperty(C.COLOR_SEC_LIGHT)
    c_sec_dark = properties.ListProperty(C.COLOR_SEC_DARK)

    def _install_settings_keys(self, window):
        # we don't want default Kivy's behaviour of displaying
        # a settings screen when pressing F1 or platform specific key
        return

    def build(self):
        Window.bind(on_keyboard=self.key_input)
        wid = CagouRootWidget(Label(text=u"Loading please wait"))
        if sys.platform == 'android':
            # we don't want menu on Android
            wid.root_menus.height = 0
        return wid

    def showWidget(self):
        self._profile_manager = ProfileManager()
        self.root.changeWidget(self._profile_manager)

    def expand(self, path, *args, **kwargs):
        """expand path and replace known values

        useful in kv. Values which can be used:
            - {media}: media dir
        @param path(unicode): path to expand
        @param *args: additional arguments used in format
        @param **kwargs: additional keyword arguments used in format
        """
        return os.path.expanduser(path).format(*args, media=self.host.media_dir, **kwargs)

    def on_start(self):
        if sys.platform == "android":
            # XXX: we use memory map instead of bridge because if we
            #      try to call a bridge method in on_pause method, the call data
            #      is not written before the actual pause
            # we create a memory map on .cagou_status file with a 1 byte status
            # status is:
            # R => running
            # P => paused
            # S => stopped
            self._first_pause = True
            self.cagou_status_fd = open('.cagou_status', 'wb+')
            self.cagou_status_fd.write('R')
            self.cagou_status_fd.flush()
            self.cagou_status = mmap.mmap(self.cagou_status_fd.fileno(), 1,
                                          prot=mmap.PROT_WRITE)

    def on_pause(self):
        self.cagou_status[0] = 'P'
        return True

    def on_resume(self):
        self.cagou_status[0] = 'R'

    def on_stop(self):
        if sys.platform == "android":
            self.cagou_status[0] = 'S'
            self.cagou_status.flush()
            self.cagou_status_fd.close()

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            # we disable [esc] handling, because default action is to quit app
            return True
        elif key == 292:
            # F11: full screen
            if not Window.fullscreen:
                window.fullscreen = 'auto'
            else:
                window.fullscreen = False
            return True
        elif key == 109 and modifier == ['alt']:
            # M-m we hide/show menu
            menu = self.root.root_menus
            if menu.height:
                Animation(height=0, duration=0.3).start(menu)
            else:
                Animation(height=menu.HEIGHT, duration=0.3).start(menu)
            return True
        elif key == 110 and modifier == ['alt']:
            # M-n we hide/show notifications
            head = self.root.head_widget
            if head.height:
                Animation(height=0, opacity=0, duration=0.3).start(head)
            else:
                Animation(height=head.HEIGHT, opacity=1, duration=0.3).start(head)
            return True
        else:
            return False


class Cagou(QuickApp):
    MB_HANDLE = False

    def __init__(self):
        if bridge_name == 'embedded':
            from sat.core import sat_main
            self.sat = sat_main.SAT()
        if sys.platform == 'android':
            from jnius import autoclass
            service = autoclass('org.salutatoi.cagou.cagou.ServiceBackend')
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            argument = ''
            service.start(mActivity, argument)
            self.service = service

        bridge_module = dynamic_import.bridge(bridge_name, 'sat_frontends.bridge')
        if bridge_module is None:
            log.error(u"Can't import {} bridge".format(bridge_name))
            sys.exit(3)
        else:
            log.debug(u"Loading {} bridge".format(bridge_name))
        super(Cagou, self).__init__(bridge_factory=bridge_module.Bridge,
                                    xmlui=xmlui,
                                    check_options=quick_utils.check_options,
                                    connect_bridge=False)
        self._import_kv()
        self.app = CagouApp()
        self.app.host = self
        self.media_dir = self.app.media_dir = config.getConfig(main_config, '',
                                                               'media_dir')
        self.downloads_dir = self.app.downloads_dir = config.getConfig(main_config, '',
                                                                       'downloads_dir')
        if not os.path.exists(self.downloads_dir):
            try:
                os.makedirs(self.downloads_dir)
            except OSError as e:
                log.warnings(_(u"Can't create downloads dir: {reason}").format(reason=e))
        self.app.default_avatar = os.path.join(self.media_dir, "misc/default_avatar.png")
        self.app.icon = os.path.join(self.media_dir,
                                     "icons/muchoslava/png/cagou_profil_bleu_96.png")
        self._plg_wids = []  # main widgets plugins
        self._plg_wids_transfer = []  # transfer widgets plugins
        self._import_plugins()
        self._visible_widgets = {}  # visible widgets by classes

    @property
    def visible_widgets(self):
        for w_list in self._visible_widgets.itervalues():
            for w in w_list:
                yield w

    def onBridgeConnected(self):
        super(Cagou, self).onBridgeConnected()
        self.registerSignal("otrState", iface="plugin")
        self.bridge.getReady(self.onBackendReady)

    def _bridgeEb(self, failure):
        if bridge_name == "pb" and sys.platform == "android":
            try:
                self.retried += 1
            except AttributeError:
                self.retried = 1
            from twisted.internet.error import ConnectionRefusedError
            if failure.check(ConnectionRefusedError) and self.retried < 100:
                if self.retried % 20 == 0:
                    log.debug("backend not ready, retrying ({})".format(self.retried))
                Clock.schedule_once(lambda dummy: self.connectBridge(), 0.05)
                return
        super(Cagou, self)._bridgeEb(failure)

    def run(self):
        self.connectBridge()
        self.app.bind(on_stop=self.onStop)
        self.app.run()

    def onStop(self, obj):
        try:
            sat_instance = self.sat
        except AttributeError:
            pass
        else:
            sat_instance.stopService()

    def onBackendReady(self):
        self.app.showWidget()
        self.postInit()

    def postInit(self, dummy=None):
        # FIXME: resize seem to bug on android, so we use below_target for now
        self.app.root_window.softinput_mode = "below_target"
        profile_manager = self.app._profile_manager
        del self.app._profile_manager
        super(Cagou, self).postInit(profile_manager)

    def _defaultFactoryMain(self, plugin_info, target, profiles):
        """default factory used to create main widgets instances

        used when PLUGIN_INFO["factory"] is not set
        @param plugin_info(dict): plugin datas
        @param target: QuickWidget target
        @param profiles(iterable): list of profiles
        """
        main_cls = plugin_info['main']
        return self.widgets.getOrCreateWidget(main_cls,
                                              target,
                                              on_new_widget=None,
                                              profiles=iter(self.profiles))

    def _defaultFactoryTransfer(self, plugin_info, callback, cancel_cb, profiles):
        """default factory used to create transfer widgets instances

        @param plugin_info(dict): plugin datas
        @param callback(callable): method to call with path to file to transfer
        @param cancel_cb(callable): call when transfer is cancelled
            transfer widget must be used as first argument
        @param profiles(iterable): list of profiles
            None if not specified
        """
        main_cls = plugin_info['main']
        return main_cls(callback=callback, cancel_cb=cancel_cb)

    ## plugins & kv import ##

    def _import_kv(self):
        """import all kv files in cagou.kv"""
        path = os.path.dirname(cagou.kv.__file__)
        kv_files = glob.glob(os.path.join(path, "*.kv"))
        # we want to be sure that base.kv is loaded first
        # as it override some Kivy widgets properties
        for kv_file in kv_files:
            if kv_file.endswith('base.kv'):
                kv_files.remove(kv_file)
                kv_files.insert(0, kv_file)
                break
        else:
            raise exceptions.InternalError("base.kv is missing")

        for kv_file in kv_files:
            Builder.load_file(kv_file)
            log.debug(u"kv file {} loaded".format(kv_file))

    def _import_plugins(self):
        """import all plugins"""
        self.default_wid = None
        plugins_path = os.path.dirname(cagou.plugins.__file__)
        plugin_glob = u"plugin*." + C.PLUGIN_EXT
        plug_lst = [os.path.splitext(p)[0] for p in
                    map(os.path.basename, glob.glob(os.path.join(plugins_path,
                                                                 plugin_glob)))]

        imported_names_main = set()  # used to avoid loading 2 times
                                     # plugin with same import name
        imported_names_transfer = set()
        for plug in plug_lst:
            plugin_path = 'cagou.plugins.' + plug

            # we get type from plugin name
            suff = plug[7:]
            if u'_' not in suff:
                log.error(u"invalid plugin name: {}, skipping".format(plug))
                continue
            plugin_type = suff[:suff.find(u'_')]

            # and select the variable to use according to type
            if plugin_type == C.PLUG_TYPE_WID:
                imported_names = imported_names_main
                default_factory = self._defaultFactoryMain
            elif plugin_type == C.PLUG_TYPE_TRANSFER:
                imported_names = imported_names_transfer
                default_factory = self._defaultFactoryTransfer
            else:
                log.error(u"unknown plugin type {type_} for plugin {file_}, skipping"
                    .format(
                    type_ = plugin_type,
                    file_ = plug
                    ))
                continue
            plugins_set = self._getPluginsSet(plugin_type)

            mod = import_module(plugin_path)
            try:
                plugin_info = mod.PLUGIN_INFO
            except AttributeError:
                plugin_info = {}

            plugin_info['plugin_file'] = plug
            plugin_info['plugin_type'] = plugin_type

            if 'platforms' in plugin_info:
                if sys.platform not in plugin_info['platforms']:
                    log.info(u"{plugin_file} is not used on this platform, skipping"
                             .format(**plugin_info))
                    continue

            # import name is used to differentiate plugins
            if 'import_name' not in plugin_info:
                plugin_info['import_name'] = plug
            if plugin_info['import_name'] in imported_names:
                log.warning(_(u"there is already a plugin named {}, "
                              u"ignoring new one").format(plugin_info['import_name']))
                continue
            if plugin_info['import_name'] == C.WID_SELECTOR:
                if plugin_type != C.PLUG_TYPE_WID:
                    log.error(u"{import_name} import name can only be used with {type_} "
                              u"type, skipping {name}".format(type_=C.PLUG_TYPE_WID,
                                                              **plugin_info))
                    continue
                # if WidgetSelector exists, it will be our default widget
                self.default_wid = plugin_info

            # we want everything optional, so we use plugin file name
            # if actual name is not found
            if 'name' not in plugin_info:
                name_start = 8 + len(plugin_type)
                plugin_info['name'] = plug[name_start:]

            # we need to load the kv file
            if 'kv_file' not in plugin_info:
                plugin_info['kv_file'] = u'{}.kv'.format(plug)
            kv_path = os.path.join(plugins_path, plugin_info['kv_file'])
            if not os.path.exists(kv_path):
                log.debug(u"no kv found for {plugin_file}".format(**plugin_info))
            else:
                Builder.load_file(kv_path)

            # what is the main class ?
            main_cls = getattr(mod, plugin_info['main'])
            plugin_info['main'] = main_cls

            # factory is used to create the instance
            # if not found, we use a defaut one with getOrCreateWidget
            if 'factory' not in plugin_info:
                plugin_info['factory'] = default_factory

            # icons
            for size in ('small', 'medium'):
                key = u'icon_{}'.format(size)
                try:
                    path = plugin_info[key]
                except KeyError:
                    path = C.DEFAULT_WIDGET_ICON.format(media=self.media_dir)
                else:
                    path = path.format(media=self.media_dir)
                    if not os.path.isfile(path):
                        path = C.DEFAULT_WIDGET_ICON.format(media=self.media_dir)
                plugin_info[key] = path

            plugins_set.append(plugin_info)
        if not self._plg_wids:
            log.error(_(u"no widget plugin found"))
            return

        # we want widgets sorted by names
        self._plg_wids.sort(key=lambda p: p['name'].lower())
        self._plg_wids_transfer.sort(key=lambda p: p['name'].lower())

        if self.default_wid is None:
            # we have no selector widget, we use the first widget as default
            self.default_wid = self._plg_wids[0]

    def _getPluginsSet(self, type_):
        if type_ == C.PLUG_TYPE_WID:
            return self._plg_wids
        elif type_ == C.PLUG_TYPE_TRANSFER:
            return self._plg_wids_transfer
        else:
            raise KeyError(u"{} plugin type is unknown".format(type_))

    def getPluggedWidgets(self, type_=C.PLUG_TYPE_WID, except_cls=None):
        """get available widgets plugin infos

        @param type_(unicode): type of widgets to get
            one of C.PLUG_TYPE_* constant
        @param except_cls(None, class): if not None,
            widgets from this class will be excluded
        @return (iter[dict]): available widgets plugin infos
        """
        plugins_set = self._getPluginsSet(type_)
        for plugin_data in plugins_set:
            if plugin_data['main'] == except_cls:
                continue
            yield plugin_data

    def getPluginInfo(self, type_=C.PLUG_TYPE_WID, **kwargs):
        """get first plugin info corresponding to filters

        @param type_(unicode): type of widgets to get
            one of C.PLUG_TYPE_* constant
        @param **kwargs: filter(s) to use, each key present here must also
            exist and be of the same value in requested plugin info
        @return (dict, None): found plugin info or None
        """
        plugins_set = self._getPluginsSet(type_)
        for plugin_info in plugins_set:
            for k, w in kwargs.iteritems():
                try:
                    if plugin_info[k] != w:
                        continue
                except KeyError:
                    continue
                return plugin_info

    ## widgets handling

    def newWidget(self, widget):
        log.debug(u"new widget created: {}".format(widget))
        if isinstance(widget, quick_chat.QuickChat) and widget.type == C.CHAT_GROUP:
            self.addNote(u"", _(u"room {} has been joined").format(widget.target))

    def switchWidget(self, old, new):
        """Replace old widget by new one

        old(CagouWidget): CagouWidget instance or a child
        new(CagouWidget): new widget instance
        """
        to_change = None
        if isinstance(old, CagouWidget):
            to_change = old
        else:
            for w in old.walk_reverse():
                if isinstance(w, CagouWidget):
                    to_change = w
                    break

        if to_change is None:
            raise exceptions.InternalError(u"no CagouWidget found when "
                                           u"trying to switch widget")

        wrapper = to_change.parent
        while wrapper is not None and not(isinstance(wrapper, widgets_handler.WHWrapper)):
            wrapper = wrapper.parent

        if wrapper is None:
            raise exceptions.InternalError(u"no wrapper found")

        wrapper.changeWidget(new)

    def addVisibleWidget(self, widget):
        """declare a widget visible

        for internal use only!
        """
        assert isinstance(widget, quick_widgets.QuickWidget)
        self._visible_widgets.setdefault(widget.__class__, []).append(widget)

    def removeVisibleWidget(self, widget):
        """declare a widget not visible anymore

        for internal use only!
        """
        self._visible_widgets[widget.__class__].remove(widget)
        self.widgets.deleteWidget(widget)

    def getVisibleList(self, cls):
        """get list of visible widgets for a given class

        @param cls(QuickWidget class): type of widgets to get
        @return (list[QuickWidget class]): visible widgets of this class
        """
        try:
            return self._visible_widgets[cls]
        except KeyError:
            return []

    def getOrClone(self, widget):
        """Get a QuickWidget if it has not parent set else clone it"""
        if widget.parent is None:
            return widget
        targets = list(widget.targets)
        w = self.widgets.getOrCreateWidget(widget.__class__,
                                           targets[0],
                                           on_new_widget=None,
                                           on_existing_widget=C.WIDGET_RECREATE,
                                           profiles=widget.profiles)
        for t in targets[1:]:
            w.addTarget(t)
        return w

    ## menus ##

    def _menusGetCb(self, backend_menus):
        main_menu = self.app.root.root_menus
        self.menus.addMenus(backend_menus)
        self.menus.addMenu(C.MENU_GLOBAL,
                           (_(u"Help"), _(u"About")),
                           callback=main_menu.onAbout)
        main_menu.update(C.MENU_GLOBAL)

    ## bridge handlers ##

    def otrStateHandler(self, state, dest_jid, profile):
        """OTR state has changed for on destinee"""
        # XXX: this method could be in QuickApp but it's here as
        #      it's only used by Cagou so far
        for widget in self.widgets.getWidgets(quick_chat.QuickChat, profiles=(profile,)):
            widget.onOTRState(state, dest_jid, profile)

    ## misc ##

    def plugging_profiles(self):
        self.app.root.changeWidget(widgets_handler.WidgetsHandler())
        self.bridge.menusGet("", C.NO_SECURITY_LIMIT, callback=self._menusGetCb)

    def setPresenceStatus(self, show='', status=None, profile=C.PROF_KEY_NONE):
        log.info(u"Profile presence status set to {show}/{status}".format(show=show,
                                                                          status=status))

    def errback(self, failure_, title=_('error'),
                message=_(u'error while processing: {msg}')):
        self.addNote(title, message.format(msg=failure_), level=C.XMLUI_DATA_LVL_WARNING)

    def addNote(self, title, message, level=C.XMLUI_DATA_LVL_INFO):
        """add a note (message which disappear) to root widget's header"""
        self.app.root.addNote(title, message, level)

    def addNotifUI(self, ui):
        """add a notification with a XMLUI attached

        @param ui(xmlui.XMLUIPanel): XMLUI instance to show when notification is selected
        """
        self.app.root.addNotifUI(ui)

    def addNotifWidget(self, widget):
        """add a notification with a Kivy widget attached

        @param widget(kivy.uix.Widget): widget to attach to notification
        """
        self.app.root.addNotifWidget(widget)

    def showUI(self, ui):
        """show a XMLUI"""
        self.app.root.changeWidget(ui, "xmlui")
        self.app.root.show("xmlui")

    def showExtraUI(self, widget):
        """show any extra widget"""
        self.app.root.changeWidget(widget, "extra")
        self.app.root.show("extra")

    def closeUI(self):
        self.app.root.show()

    def getDefaultAvatar(self, entity=None):
        return self.app.default_avatar

    def _dialog_cb(self, cb, *args, **kwargs):
        """generic dialog callback

        close dialog then call the callback with given arguments
        """
        def callback():
            self.closeUI()
            cb(*args, **kwargs)
        return callback

    def showDialog(self, message, title, type="info", answer_cb=None, answer_data=None):
        if type in ('info', 'warning', 'error'):
            self.addNote(title, message, type)
        elif type == "yes/no":
            wid = dialog.ConfirmDialog(title=title, message=message,
                                       yes_cb=self._dialog_cb(answer_cb,
                                                              True,
                                                              answer_data),
                                       no_cb=self._dialog_cb(answer_cb,
                                                             False,
                                                             answer_data)
                                       )
            self.addNotifWidget(wid)
        else:
            log.warning(_(u"unknown dialog type: {dialog_type}").format(dialog_type=type))


    def desktop_notif(self, message, title=u'', duration=5000):
        if notification is not None:
            try:
                notification.notify(title=title,
                                    message=message,
                                    app_name=C.APP_NAME,
                                    app_icon=self.app.icon,
                                    timeout = duration)
            except Exception as e:
                log.warning(_(u"Can't use notifications, disabling: {msg}").format(
                    msg = e))
                global notification
                notification = None

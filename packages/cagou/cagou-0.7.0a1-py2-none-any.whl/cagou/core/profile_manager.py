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
log = logging.getLogger(__name__)
from .constants import Const as C
from sat_frontends.quick_frontend.quick_profile_manager import QuickProfileManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix import listview
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.adapters import listadapter
from kivy.metrics import sp
from kivy import properties
from cagou import G


class ProfileItem(listview.ListItemButton):
    pass


class ProfileListAdapter(listadapter.ListAdapter):

    def __init__(self, pm, *args, **kwargs):
        super(ProfileListAdapter, self).__init__(*args, **kwargs)
        self.pm = pm

    def closeUI(self, xmlui):
        self.pm.screen_manager.transition.direction = 'right'
        self.pm.screen_manager.current = 'profiles'

    def showUI(self, xmlui):
        xmlui.setCloseCb(self.closeUI)
        if xmlui.type == 'popup':
            xmlui.bind(on_touch_up=lambda obj, value: self.closeUI(xmlui))
        self.pm.xmlui_screen.clear_widgets()
        self.pm.xmlui_screen.add_widget(xmlui)
        self.pm.screen_manager.transition.direction = 'left'
        self.pm.screen_manager.current = 'xmlui'

    def select_item_view(self, view):
        def authenticate_cb(data, cb_id, profile):
            if C.bool(data.pop('validated', C.BOOL_FALSE)):
                super(ProfileListAdapter, self).select_item_view(view)
            G.host.actionManager(data, callback=authenticate_cb, ui_show_cb=self.showUI, profile=profile)

        G.host.launchAction(C.AUTHENTICATE_PROFILE_ID, callback=authenticate_cb, profile=view.text)


class ConnectButton(Button):

    def __init__(self, profile_screen):
        self.profile_screen = profile_screen
        self.pm = profile_screen.pm
        super(ConnectButton, self).__init__()


class NewProfileScreen(Screen):
    profile_name = properties.ObjectProperty(None)
    jid = properties.ObjectProperty(None)
    password = properties.ObjectProperty(None)
    error_msg = properties.StringProperty('')

    def __init__(self, pm):
        super(NewProfileScreen, self).__init__(name=u'new_profile')
        self.pm = pm

    def onCreationFailure(self, failure):
        msg = [l for l in unicode(failure).split('\n') if l][-1]
        self.error_msg = unicode(msg)

    def onCreationSuccess(self, profile):
        self.pm.profiles_screen.reload()
        G.host.bridge.profileStartSession(self.password.text, profile, callback=lambda dummy: self._sessionStarted(profile), errback=self.onCreationFailure)

    def _sessionStarted(self, profile):
        jid = self.jid.text.strip()
        G.host.bridge.setParam("JabberID", jid, "Connection", -1, profile)
        G.host.bridge.setParam("Password", self.password.text, "Connection", -1, profile)
        self.pm.screen_manager.transition.direction = 'right'
        self.pm.screen_manager.current = 'profiles'

    def doCreate(self):
        name = self.profile_name.text.strip()
        # XXX: we use XMPP password for profile password to simplify
        #      if user want to change profile password, he can do it in preferences
        G.host.bridge.profileCreate(name, self.password.text, u'', callback=lambda: self.onCreationSuccess(name), errback=self.onCreationFailure)


class DeleteProfilesScreen(Screen):

    def __init__(self, pm):
        self.pm = pm
        super(DeleteProfilesScreen, self).__init__(name=u'delete_profiles')

    def doDelete(self):
        """This method will delete *ALL* selected profiles"""
        to_delete = self.pm.getProfiles()
        deleted = [0]

        def deleteInc():
            deleted[0] += 1
            if deleted[0] == len(to_delete):
                self.pm.profiles_screen.reload()
                self.pm.screen_manager.transition.direction = 'right'
                self.pm.screen_manager.current = 'profiles'

        for profile in to_delete:
            log.info(u"Deleteing profile [{}]".format(profile))
            G.host.bridge.asyncDeleteProfile(profile, callback=deleteInc, errback=deleteInc)


class ProfilesScreen(Screen):
    layout = properties.ObjectProperty(None)

    def __init__(self, pm):
        self.pm = pm
        self.list_adapter = ProfileListAdapter(pm,
                                               data=[],
                                               cls=ProfileItem,
                                               args_converter=self.converter,
                                               selection_mode='multiple',
                                               allow_empty_selection=True,
                                              )
        super(ProfilesScreen, self).__init__(name=u'profiles')
        self.layout.add_widget(listview.ListView(adapter=self.list_adapter))
        connect_btn = ConnectButton(self)
        self.layout.add_widget(connect_btn)
        self.reload()

    def _profilesListGetCb(self, profiles):
        profiles.sort()
        self.list_adapter.data = profiles

    def converter(self, row_idx, obj):
        return {'text': obj,
                'size_hint_y': None,
                'height': sp(40)}

    def reload(self):
        """Reload profiles list"""
        G.host.bridge.profilesListGet(callback=self._profilesListGetCb)


class ProfileManager(QuickProfileManager, BoxLayout):

    def __init__(self, autoconnect=None):
        QuickProfileManager.__init__(self, G.host, autoconnect)
        BoxLayout.__init__(self, orientation="vertical")
        self.screen_manager = ScreenManager()
        self.profiles_screen = ProfilesScreen(self)
        self.new_profile_screen = NewProfileScreen(self)
        self.delete_profiles_screen = DeleteProfilesScreen(self)
        self.xmlui_screen = Screen(name=u'xmlui')
        self.screen_manager.add_widget(self.profiles_screen)
        self.screen_manager.add_widget(self.xmlui_screen)
        self.screen_manager.add_widget(self.new_profile_screen)
        self.screen_manager.add_widget(self.delete_profiles_screen)
        self.add_widget(self.screen_manager)

    def getProfiles(self):
        return [pi.text for pi in self.profiles_screen.list_adapter.selection]

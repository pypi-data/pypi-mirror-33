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


from sat.core.i18n import _
from sat.core import log as logging
log = logging.getLogger(__name__)
from cagou.core.constants import Const as C
from cagou.core.common import JidToggle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from cagou.core.utils import FilterBehavior
from kivy import properties
from kivy.garden import contextmenu, modernmenu
from sat_frontends.quick_frontend import quick_menus
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.clock import Clock
from cagou import G
from functools import partial
import webbrowser

ABOUT_TITLE = _(u"About {}".format(C.APP_NAME))
ABOUT_CONTENT = _(u"""Cagou (Salut à Toi) v{version}

Cagou is a libre communication tool based on libre standard XMPP.

Cagou is part of the "Salut à Toi" project
more informations at [color=5500ff][ref=website]salut-a-toi.org[/ref][/color]
""").format(version=C.APP_VERSION)


class AboutContent(Label):

    def on_ref_press(self, value):
        if value == "website":
            webbrowser.open("https://salut-a-toi.org")


class AboutPopup(Popup):

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dismiss()
        return super(AboutPopup, self).on_touch_down(touch)


class MainMenu(contextmenu.AppMenu):
    pass


class MenuItem(contextmenu.ContextMenuTextItem):
    item = properties.ObjectProperty()

    def on_item(self, instance, item):
        self.text = item.name

    def on_release(self):
        super(MenuItem, self).on_release()
        self.parent.hide()
        selected = G.host.selected_widget
        profile = None
        if selected is not None:
            try:
                # FIXME: handle multi-profiles
                profile = next(iter(selected.profiles))
            except AttributeError:
                pass

        if profile is None:
            try:
                profile = list(selected.profiles)[0]
            except (AttributeError, IndexError):
                try:
                    profile = list(G.host.profiles)[0]
                except IndexError:
                    log.warning(u"Can't find profile")
        self.item.call(selected, profile)


class MenuSeparator(contextmenu.ContextMenuDivider):
    pass


class RootMenuContainer(contextmenu.AppMenuTextItem):
    pass


class MenuContainer(contextmenu.ContextMenuTextItem):
    pass


class MenusWidget(BoxLayout):

    def update(self, type_, caller=None):
        """Method to call when menus have changed

        @param type_(unicode): menu type like in sat.core.sat_main.importMenu
        @param caller(Widget): instance linked to the menus
        """
        self.menus_container = G.host.menus.getMainContainer(type_)
        self.createMenus(caller)

    def _buildMenus(self, container, caller=None):
        """Recursively build menus of the container

        @param container(quick_menus.MenuContainer): menu container
        @param caller(Widget): instance linked to the menus
        """
        if caller is None:
            main_menu = MainMenu()
            self.add_widget(main_menu)
            caller = main_menu
        else:
            context_menu = contextmenu.ContextMenu()
            caller.add_widget(context_menu)
            # FIXME: next line is needed after parent is set to avoid
            #        a display bug in contextmenu
            # TODO: fix this upstream
            context_menu._on_visible(False)

            caller = context_menu

        for child in container.getActiveMenus():
            if isinstance(child, quick_menus.MenuContainer):
                if isinstance(caller, MainMenu):
                    menu_container = RootMenuContainer()
                else:
                    menu_container = MenuContainer()
                menu_container.text = child.name
                caller.add_widget(menu_container)
                self._buildMenus(child, caller=menu_container)
            elif isinstance(child, quick_menus.MenuSeparator):
                wid = MenuSeparator()
                caller.add_widget(wid)
            elif isinstance(child, quick_menus.MenuItem):
                wid = MenuItem(item=child)
                caller.add_widget(wid)
            else:
                log.error(u"Unknown child type: {}".format(child))

    def createMenus(self, caller):
        self.clear_widgets()
        self._buildMenus(self.menus_container, caller)

    def onAbout(self):
        about = AboutPopup()
        about.title = ABOUT_TITLE
        about.content = AboutContent(text=ABOUT_CONTENT, markup=True)
        about.open()


class TransferItem(BoxLayout):
    plug_info = properties.DictProperty()

    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos):
            return super(TransferItem, self).on_touch_up(touch)
        else:
            transfer_menu = self.parent
            while not isinstance(transfer_menu, TransferMenu):
                transfer_menu = transfer_menu.parent
            transfer_menu.do_callback(self.plug_info)
            return True


class SideMenu(BoxLayout):
    size_hint_close = (0, 1)
    size_hint_open = (0.4, 1)
    size_close = (100, 100)
    size_open = (0, 0)
    bg_color = properties.ListProperty([0, 0, 0, 1])
    # callback will be called with arguments relevant to menu
    callback = properties.ObjectProperty()
    # call do_callback even when menu is cancelled
    callback_on_close = properties.BooleanProperty(False)
    # cancel callback need to remove the widget for UI
    # will be called with the widget to remove as argument
    cancel_cb = properties.ObjectProperty()

    def __init__(self, **kwargs):
        super(SideMenu, self).__init__(**kwargs)
        if self.cancel_cb is None:
            self.cancel_cb = self.onMenuCancelled

    def _set_anim_kw(self, kw, size_hint, size):
        """Set animation keywords

        for each value of size_hint it is used if not None,
        else size is used.
        If one value of size is bigger than the respective one of Window
        the one of Window is used
        """
        size_hint_x, size_hint_y = size_hint
        width, height = size
        if size_hint_x is not None:
            kw['size_hint_x'] = size_hint_x
        elif width is not None:
            kw['width'] = min(width, Window.width)

        if size_hint_y is not None:
            kw['size_hint_y'] = size_hint_y
        elif height is not None:
            kw['height'] = min(height, Window.height)

    def show(self, caller_wid=None):
        Window.bind(on_keyboard=self.key_input)
        G.host.app.root.add_widget(self)
        kw = {'d': 0.3, 't': 'out_back'}
        self._set_anim_kw(kw, self.size_hint_open, self.size_open)
        Animation(**kw).start(self)

    def hide(self):
        Window.unbind(on_keyboard=self.key_input)
        kw = {'d': 0.2}
        self._set_anim_kw(kw, self.size_hint_close, self.size_close)
        anim = Animation(**kw)
        anim.bind(on_complete=lambda anim, menu: self.parent.remove_widget(self))
        anim.start(self)
        if self.callback_on_close:
            self.do_callback()

    def on_touch_down(self, touch):
        # we remove the menu if we click outside
        # else we want to handle the event, but not
        # transmit it to parents
        if not self.collide_point(*touch.pos):
            self.hide()
        else:
            return super(SideMenu, self).on_touch_down(touch)
        return True

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            self.hide()
            return True

    def onMenuCancelled(self, wid, cleaning_cb=None):
        self._closeUI(wid)
        if cleaning_cb is not None:
            cleaning_cb()

    def _closeUI(self, wid):
        G.host.closeUI()

    def do_callback(self, *args, **kwargs):
        log.warning(u"callback not implemented")


class TransferMenu(SideMenu):
    """transfer menu which handle display and callbacks"""
    # callback will be called with path to file to transfer
    # profiles if set will be sent to transfer widget, may be used to get specific files
    profiles = properties.ObjectProperty()
    transfer_txt = _(u"Beware! The file will be sent to your server and stay unencrypted "
                     u"there\nServer admin(s) can see the file, and they choose how, "
                     u"when and if it will be deleted")
    send_txt = _(u"The file will be sent unencrypted directly to your contact "
                 u"(without transiting by the server), except in some cases")
    items_layout = properties.ObjectProperty()
    size_hint_close = (1, 0)
    size_hint_open = (1, 0.5)

    def __init__(self, **kwargs):
        super(TransferMenu, self).__init__(**kwargs)
        if self.profiles is None:
            self.profiles = iter(G.host.profiles)
        for plug_info in G.host.getPluggedWidgets(type_=C.PLUG_TYPE_TRANSFER):
            item = TransferItem(
                plug_info = plug_info
                )
            self.items_layout.add_widget(item)

    def do_callback(self, plug_info):
        self.parent.remove_widget(self)
        if self.callback is None:
            log.warning(u"TransferMenu callback is not set")
        else:
            wid = None
            external = plug_info.get('external', False)
            def onTransferCb(file_path, cleaning_cb=None):
                if not external:
                    self._closeUI(wid)
                self.callback(
                    file_path,
                    cleaning_cb,
                    transfer_type = (C.TRANSFER_UPLOAD
                        if self.ids['upload_btn'].state == "down" else C.TRANSFER_SEND))
            wid = plug_info['factory'](plug_info,
                                       onTransferCb,
                                       self.cancel_cb,
                                       self.profiles)
            if not external:
                G.host.showExtraUI(wid)


class EntitiesSelectorMenu(SideMenu, FilterBehavior):
    """allow to select entities from roster"""
    profiles = properties.ObjectProperty()
    layout = properties.ObjectProperty()
    instructions = properties.StringProperty(_(u"Please select entities"))
    filter_input = properties.ObjectProperty()
    size_hint_close = (None, 1)
    size_hint_open = (None, 1)
    size_open = (dp(250), 100)
    size_close = (0, 100)

    def __init__(self, **kwargs):
        super(EntitiesSelectorMenu, self).__init__(**kwargs)
        self.filter_input.bind(text=self.do_filter_input)
        if self.profiles is None:
            self.profiles = iter(G.host.profiles)
        for profile in self.profiles:
            for jid_, jid_data in G.host.contact_lists[profile].all_iter:
                jid_wid = JidToggle(
                    jid=jid_,
                    profile=profile)
                self.layout.add_widget(jid_wid)

    def do_callback(self):
        if self.callback is not None:
            jids = [c.jid for c in self.layout.children if c.state == 'down']
            self.callback(jids)

    def do_filter_input(self, filter_input, text):
        self.layout.spacing = 0 if text else dp(5)
        self.do_filter(self.layout.children,
                       text,
                       lambda c: c.jid,
                       width_cb=lambda c: c.width,
                       height_cb=lambda c: dp(70))


class TouchMenu(modernmenu.ModernMenu):
    pass


class TouchMenuItemBehaviour(object):
    """Class to use on every item where a menu may appear

    main_wid attribute must be set to the class inheriting from TouchMenuBehaviour
    do_item_action is the method called on simple click
    getMenuChoices must return a list of menus for long press
        menus there are dict as expected by ModernMenu
        (translated text, index and callback)
    """
    main_wid = properties.ObjectProperty()
    click_timeout = properties.NumericProperty(0.4)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        t = partial(self.open_menu, touch)
        touch.ud['menu_timeout'] = t
        Clock.schedule_once(t, self.click_timeout)
        return super(TouchMenuItemBehaviour, self).on_touch_down(touch)

    def do_item_action(self, touch):
        pass

    def on_touch_up(self, touch):
        if touch.ud.get('menu_timeout'):
            Clock.unschedule(touch.ud['menu_timeout'])
            if self.collide_point(*touch.pos) and self.main_wid.menu is None:
                self.do_item_action(touch)
        return super(TouchMenuItemBehaviour, self).on_touch_up(touch)

    def open_menu(self, touch, dt):
        self.main_wid.open_menu(self, touch)
        del touch.ud['menu_timeout']

    def getMenuChoices(self):
        """return choice adapted to selected item

        @return (list[dict]): choices ad expected by ModernMenu
        """
        return []


class TouchMenuBehaviour(object):
    """Class to handle a menu appearing on long press on items

    classes using this behaviour need to have a float_layout property
    pointing the main FloatLayout.
    """
    float_layout = properties.ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(TouchMenuBehaviour, self).__init__(*args, **kwargs)
        self.menu = None
        self.menu_item = None

    ## menu methods ##

    def clean_fl_children(self, layout, children):
        """insure that self.menu and self.menu_item are None when menu is dimissed"""
        if self.menu is not None and self.menu not in children:
            self.menu = self.menu_item = None

    def clear_menu(self):
        """remove menu if there is one"""
        if self.menu is not None:
            self.menu.dismiss()
            self.menu = None
            self.menu_item = None

    def open_menu(self, item, touch):
        """open menu for item

        @param item(PathWidget): item when the menu has been requested
        @param touch(kivy.input.MotionEvent): touch data
        """
        if self.menu_item == item:
            return
        self.clear_menu()
        pos = self.to_widget(*touch.pos)
        choices = item.getMenuChoices()
        if not choices:
            return
        self.menu = TouchMenu(choices=choices,
                                center=pos,
                                size_hint=(None, None))
        self.float_layout.add_widget(self.menu)
        self.menu.start_display(touch)
        self.menu_item = item

    def on_float_layout(self, wid, float_layout):
        float_layout.bind(children=self.clean_fl_children)

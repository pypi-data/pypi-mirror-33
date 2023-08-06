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
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy import properties
from cagou import G
from cagou.core.common import ActionIcon


class HeaderWidgetChoice(ButtonBehavior, BoxLayout):

    def __init__(self, cagou_widget, plugin_info):
        self.plugin_info = plugin_info
        super(HeaderWidgetChoice, self).__init__()
        self.bind(on_release=lambda btn: cagou_widget.switchWidget(plugin_info))


class HeaderWidgetCurrent(ButtonBehavior, ActionIcon):
    pass


class HeaderWidgetSelector(DropDown):

    def __init__(self, cagou_widget):
        super(HeaderWidgetSelector, self).__init__()
        for plugin_info in G.host.getPluggedWidgets(except_cls=cagou_widget.__class__):
            choice = HeaderWidgetChoice(cagou_widget, plugin_info)
            self.add_widget(choice)

    def add_widget(self, *args):
        widget = args[0]
        widget.bind(minimum_width=self.set_width)
        return super(HeaderWidgetSelector, self).add_widget(*args)

    def set_width(self, choice, minimum_width):
        self.width = max([c.minimum_width for c in self.container.children])


class CagouWidget(BoxLayout):
    header_input = properties.ObjectProperty(None)
    header_box = properties.ObjectProperty(None)

    def __init__(self):
        for p in G.host.getPluggedWidgets():
            if p['main'] == self.__class__:
                self.plugin_info = p
                break
        BoxLayout.__init__(self)
        self.selector = HeaderWidgetSelector(self)

    def switchWidget(self, plugin_info):
        self.selector.dismiss()
        factory = plugin_info["factory"]
        new_widget = factory(plugin_info, None, iter(G.host.profiles))
        G.host.switchWidget(self, new_widget)

    def onHeaderInput(self):
        log.info(u"header input text entered")

    def onHeaderInputComplete(self, wid, text):
        return

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            G.host.selected_widget = self
        return super(CagouWidget, self).on_touch_down(touch)

    def headerInputAddExtra(self, widget):
        """add a widget on the right of header input"""
        self.header_box.add_widget(widget)

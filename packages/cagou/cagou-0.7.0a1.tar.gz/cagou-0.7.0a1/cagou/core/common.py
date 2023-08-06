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

"""common widgets, which can be reused everywhere"""

from sat.core.i18n import _
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from cagou.core.constants import Const as C
from kivy import properties
from cagou import G
import json
from sat.core import log as logging

log = logging.getLogger(__name__)

UNKNOWN_SYMBOL = u'Unknown symbol name'


class IconButton(ButtonBehavior, Image):
    pass


class JidItem(BoxLayout):
    bg_color = properties.ListProperty([0.2, 0.2, 0.2, 1])
    color = properties.ListProperty([1, 1, 1, 1])

    def __init__(self, jid, profile, **kwargs):
        self.jid = jid
        self.profile = profile
        self.nick = kwargs.get('nick')
        super(JidItem, self).__init__(**kwargs)

    def getImage(self, wid):
        host = G.host
        if host.contact_lists[self.profile].isRoom(self.jid.bare):
            wid.opacity = 0
            return ""
        else:
            return (host.getAvatar(self.jid, profile=self.profile)
                or host.getDefaultAvatar(self.jid))


class JidButton(ButtonBehavior, JidItem):
    pass


class JidToggle(ToggleButtonBehavior, JidItem):
    selected_color = properties.ListProperty(C.COLOR_SEC_DARK)


class Symbol(Label):
    symbol_map = None
    symbol = properties.StringProperty()
    margin = properties.NumericProperty(0)

    def __init__(self, **kwargs):
        if self.symbol_map is None:
            with open(G.host.app.expand('{media}/fonts/fontello/config.json')) as f:
                fontello_conf = json.load(f)
            Symbol.symbol_map = {g['css']:g['code'] for g in fontello_conf['glyphs']}

        super(Symbol, self).__init__(**kwargs)

    def on_symbol(self, instance, symbol):
        try:
            code = self.symbol_map[symbol]
        except KeyError:
            log.warning(_(u"Invalid symbol {symbol}").format(symbol=symbol))
        else:
            self.text = unichr(code)


class SymbolButton(ButtonBehavior, Symbol):
    pass


class SymbolLabel(ButtonBehavior, BoxLayout):
    symbol = properties.StringProperty("")
    text = properties.StringProperty("")
    color = properties.ListProperty(C.COLOR_SEC)
    bold = properties.BooleanProperty(True)
    symbol_wid = properties.ObjectProperty()
    label = properties.ObjectProperty()


class ActionSymbol(Symbol):
    pass


class ActionIcon(BoxLayout):
    plugin_info = properties.DictProperty()

    def on_plugin_info(self, instance, plugin_info):
        self.clear_widgets()
        try:
            symbol = plugin_info['icon_symbol']
        except KeyError:
            icon_src = plugin_info['icon_medium']
            icon_wid = Image(source=icon_src, allow_stretch=True)
            self.add_widget(icon_wid)
        else:
            icon_wid = ActionSymbol(symbol=symbol)
            self.add_widget(icon_wid)

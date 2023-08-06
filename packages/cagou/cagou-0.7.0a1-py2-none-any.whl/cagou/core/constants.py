#!/usr/bin/python
# -*- coding: utf-8 -*-

# Primitivus: a SAT frontend
# Copyright (C) 2009-2016-2018 Jérôme Poisson (goffi@goffi.org)

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

from sat_frontends.quick_frontend import constants


class Const(constants.Const):
    APP_NAME = u"Cagou"
    LOG_OPT_SECTION = APP_NAME.lower()
    CONFIG_SECTION = APP_NAME.lower()
    WID_SELECTOR = u'selector'
    ICON_SIZES = (u'small', u'medium')  # small = 32, medium = 44
    DEFAULT_WIDGET_ICON = u'{media}/misc/black.png'

    PLUG_TYPE_WID = u'wid'
    PLUG_TYPE_TRANSFER = u'transfer'

    TRANSFER_UPLOAD = u"upload"
    TRANSFER_SEND = u"send"

    COLOR_PRIM = [0.98, 0.98, 0.98, 1]
    COLOR_PRIM_LIGHT = [1, 1, 1, 1]
    COLOR_PRIM_DARK = [0.78, 0.78, 0.78, 1]
    COLOR_SEC = [0.27, 0.54, 1.0, 1]
    COLOR_SEC_LIGHT = [0.51, 0.73, 1.0, 1]
    COLOR_SEC_DARK = [0.0, 0.37, 0.8, 1]

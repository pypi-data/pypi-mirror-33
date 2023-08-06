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

import sys
import os
# we want the service to access the modules from parent dir (sat, etc.)
os.chdir('..')
sys.path.insert(0, '')
from sat.core.constants import Const as C
from sat.core import log_config
# SàT log conf must be done before calling Kivy
log_config.satConfigure(C.LOG_BACKEND_STANDARD, C)
# if this module is called, we should be on android,
# but just in case...
from kivy import utils as kivy_utils
if kivy_utils.platform == "android":
    # sys.platform is "linux" on android by default
    # so we change it to allow backend to detect android
    sys.platform = "android"
    C.PLUGIN_EXT = "pyo"
from sat.core import sat_main
from twisted.internet import reactor

sat = sat_main.SAT()
reactor.run()

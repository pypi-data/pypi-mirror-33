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

import os.path


version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
with open(version_file) as f:
    __version__ = f.read().strip()

class Global(object):
    @property
    def host(self):
        return self._host
G = Global()

# this import must be done after G is created
from core import cagou_main

def run():
    host = G._host = cagou_main.Cagou()
    host.run()

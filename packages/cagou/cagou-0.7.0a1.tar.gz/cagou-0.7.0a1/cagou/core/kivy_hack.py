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

CONF_KIVY_LEVEL = 'log_kivy_level'


def do_hack():
    """work around Kivy hijacking of logs and arguments"""
    # we remove args so kivy doesn't use them
    # this is need to avoid kivy breaking QuickApp args handling
    import sys
    ori_argv = sys.argv[:]
    sys.argv = sys.argv[:1]
    from constants import Const as C
    from sat.core import log_config
    log_config.satConfigure(C.LOG_BACKEND_STANDARD, C)

    import config
    kivy_level = config.getConfig(C.CONFIG_SECTION, CONF_KIVY_LEVEL, 'follow').upper()

    # kivy handles its own loggers, we don't want that!
    import logging
    root_logger = logging.root
    kivy_logger = logging.getLogger('kivy')
    ori_addHandler = kivy_logger.addHandler
    kivy_logger.addHandler = lambda dummy: None
    ori_setLevel = kivy_logger.setLevel
    if kivy_level == 'FOLLOW':
        # level is following SàT level
        kivy_logger.setLevel = lambda level: None
    elif kivy_level == 'KIVY':
        # level will be set by Kivy according to its own conf
        pass
    elif kivy_level in C.LOG_LEVELS:
        kivy_logger.setLevel(kivy_level)
        kivy_logger.setLevel = lambda level: None
    else:
        raise ValueError(u"Unknown value for {name}: {value}".format(name=CONF_KIVY_LEVEL, value=kivy_level))

    # during import kivy set its logging stuff
    import kivy
    kivy # to avoid pyflakes warning

    # we want to separate kivy logs from other logs
    logging.root = root_logger
    from kivy import logger
    sys.stderr = logger.previous_stderr

    # we restore original methods
    kivy_logger.addHandler = ori_addHandler
    kivy_logger.setLevel = ori_setLevel

    # we restore original arguments
    sys.argv = ori_argv

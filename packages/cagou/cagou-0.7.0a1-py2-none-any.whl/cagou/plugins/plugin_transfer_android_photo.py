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
from sat.core.i18n import _
import sys
import os
import os.path
import time
if sys.platform == "android":
    from plyer import camera
    from jnius import autoclass
    Environment = autoclass('android.os.Environment')
else:
    import tempfile


PLUGIN_INFO = {
    "name": _(u"take photo"),
    "main": "AndroidPhoto",
    "platforms": ('android',),
    "external": True,
    "description": _(u"upload a photo from photo application"),
    "icon_medium": u"{media}/icons/muchoslava/png/camera_off_50.png",
}


class AndroidPhoto(object):

    def __init__(self, callback, cancel_cb):
        self.callback = callback
        self.cancel_cb = cancel_cb
        filename = time.strftime("%Y-%m-%d_%H:%M:%S.jpg", time.gmtime())
        tmp_dir = self.getTmpDir()
        tmp_file = os.path.join(tmp_dir, filename)
        log.debug(u"Picture will be saved to {}".format(tmp_file))
        camera.take_picture(tmp_file, self.callback)
        # we don't delete the file, as it is nice to keep it locally

    def getTmpDir(self):
        if sys.platform == "android":
            dcim_path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM).getAbsolutePath()
            return dcim_path
        else:
            return tempfile.mkdtemp()

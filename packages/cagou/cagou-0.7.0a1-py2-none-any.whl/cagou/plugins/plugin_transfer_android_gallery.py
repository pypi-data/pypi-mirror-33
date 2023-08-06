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
import tempfile
import os
import os.path
if sys.platform=="android":
    from jnius import autoclass
    from android import activity, mActivity

    Intent = autoclass('android.content.Intent')
    OpenableColumns = autoclass('android.provider.OpenableColumns')
    PHOTO_GALLERY = 1
    RESULT_OK = -1



PLUGIN_INFO = {
    "name": _(u"gallery"),
    "main": "AndroidGallery",
    "platforms": ('android',),
    "external": True,
    "description": _(u"upload a photo from photo gallery"),
    "icon_medium": u"{media}/icons/muchoslava/png/gallery_50.png",
}


class AndroidGallery(object):

    def __init__(self, callback, cancel_cb):
        self.callback = callback
        self.cancel_cb = cancel_cb
        activity.bind(on_activity_result=self.on_activity_result)
        intent = Intent()
        intent.setType('image/*')
        intent.setAction(Intent.ACTION_GET_CONTENT)
        mActivity.startActivityForResult(intent, PHOTO_GALLERY);

    def on_activity_result(self, requestCode, resultCode, data):
        # TODO: move file dump to a thread or use async callbacks during file writting
        if requestCode == PHOTO_GALLERY and resultCode == RESULT_OK:
            if data is None:
                log.warning(u"No data found in activity result")
                self.cancel_cb(self, None)
                return
            uri = data.getData()

            # we get filename in the way explained at https://developer.android.com/training/secure-file-sharing/retrieve-info.html
            cursor = mActivity.getContentResolver().query(uri, None, None, None, None )
            name_idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            cursor.moveToFirst()
            filename = cursor.getString(name_idx)

            # we save data in a temporary file that we send to callback
            # the file will be removed once upload is done (or if an error happens)
            input_stream = mActivity.getContentResolver().openInputStream(uri)
            tmp_dir = tempfile.mkdtemp()
            tmp_file = os.path.join(tmp_dir, filename)
            def cleaning():
                os.unlink(tmp_file)
                os.rmdir(tmp_dir)
                log.debug(u'temporary file cleaned')
            buff = bytearray(4096)
            with open(tmp_file, 'wb') as f:
                while True:
                    ret = input_stream.read(buff, 0, 4096)
                    if ret != -1:
                        f.write(buff)
                    else:
                        break
            input_stream.close()
            self.callback(tmp_file, cleaning)
        else:
            self.cancel_cb(self, None)

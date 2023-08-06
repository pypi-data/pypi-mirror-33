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
from kivy.uix import image as kivy_img
from kivy.core.image import Image as CoreImage
from kivy.resources import resource_find
import io
import PIL


class Image(kivy_img.Image):
    """Image widget which accept source without extension"""

    def texture_update(self, *largs):
        if not self.source:
            self.texture = None
        else:
            filename = resource_find(self.source)
            self._loops = 0
            if filename is None:
                return log.error('Image: Error reading file {filename}'.
                                    format(filename=self.source))
            mipmap = self.mipmap
            if self._coreimage is not None:
                self._coreimage.unbind(on_texture=self._on_tex_change)
            try:
                self._coreimage = ci = CoreImage(filename, mipmap=mipmap,
                                                 anim_delay=self.anim_delay,
                                                 keep_data=self.keep_data,
                                                 nocache=self.nocache)
            except Exception as e:
                # loading failed probably because of unmanaged extention,
                # we try our luck with with PIL
                try:
                    im = PIL.Image.open(filename)
                    ext = im.format.lower()
                    del im
                    # we can't use im.tobytes as it would use the
                    # internal decompressed representation from pillow
                    # and im.save would need processing to handle format
                    data = io.BytesIO(open(filename, "rb").read())
                    cache_filename = u"{}.{}".format(filename,ext) # needed for kivy's Image to use cache
                    self._coreimage = ci = CoreImage(data, ext=ext,
                                                     filename=cache_filename, mipmap=mipmap,
                                                     anim_delay=self.anim_delay,
                                                     keep_data=self.keep_data,
                                                     nocache=self.nocache)
                except Exception as e:
                    log.warning(u"Can't load image: {}".format(e))
                    self._coreimage = ci = None

            if ci:
                ci.bind(on_texture=self._on_tex_change)
                self.texture = ci.texture


class AsyncImage(kivy_img.AsyncImage):
    """AsyncImage which accept file:// schema"""

    def _load_source(self, *args):
        if self.source.startswith('file://'):
            self.source = self.source[7:]
        else:
            super(AsyncImage, self)._load_source(*args)

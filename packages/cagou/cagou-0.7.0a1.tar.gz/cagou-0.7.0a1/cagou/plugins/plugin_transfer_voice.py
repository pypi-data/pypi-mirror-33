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
from kivy.uix.boxlayout import BoxLayout
import sys
import time
from kivy.clock import Clock
from kivy import properties
if sys.platform == "android":
    from plyer import audio


PLUGIN_INFO = {
    "name": _(u"voice"),
    "main": "VoiceRecorder",
    "platforms": ["android"],
    "description": _(u"transmit a voice record"),
    "icon_medium": u"{media}/icons/muchoslava/png/micro_off_50.png",
}


class VoiceRecorder(BoxLayout):
    callback = properties.ObjectProperty()
    cancel_cb = properties.ObjectProperty()
    recording = properties.BooleanProperty(False)
    playing = properties.BooleanProperty(False)
    time = properties.NumericProperty(0)

    def __init__(self, **kwargs):
        super(VoiceRecorder, self).__init__(**kwargs)
        self._started_at = None
        self._counter_timer = None
        self._play_timer = None
        self.record_time = None
        self.audio = audio
        self.audio.file_path = "/sdcard/cagou_record.3gp"

    def _updateTimer(self, dt):
        self.time = int(time.time() - self._started_at)

    def switchRecording(self):
        if self.playing:
            self._stopPlaying()
        if self.recording:
            try:
                audio.stop()
            except Exception as e:
                # an exception can happen if record is pressed
                # repeatedly in a short time (not a normal use)
                log.warning(u"Exception on stop: {}".format(e))
            self._counter_timer.cancel()
            self.time = self.time + 1
        else:
            audio.start()
            self._started_at = time.time()
            self.time = 0
            self._counter_timer = Clock.schedule_interval(self._updateTimer, 1)

        self.recording = not self.recording

    def _stopPlaying(self, dummy=None):
        if self.record_time is None:
            log.error("_stopPlaying should no be called when record_time is None")
            return
        audio.stop()
        self.playing = False
        self.time = self.record_time
        if self._counter_timer is not None:
            self._counter_timer.cancel()

    def playRecord(self):
        if self.recording:
            return
        if self.playing:
            self._stopPlaying()
        else:
            try:
                audio.play()
            except Exception as e:
                # an exception can happen in the same situation
                # as for audio.stop() above (i.e. bad record)
                log.warning(u"Exception on play: {}".format(e))
                self.time = 0
                return

            self.playing = True
            self.record_time = self.time
            Clock.schedule_once(self._stopPlaying, self.time + 1)
            self._started_at = time.time()
            self.time = 0
            self._counter_timer =  Clock.schedule_interval(self._updateTimer, 0.5)

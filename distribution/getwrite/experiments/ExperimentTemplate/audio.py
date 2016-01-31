# -*- coding: utf-8 -*-
#
# This file is part of the OpenHandWrite project software.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import division

import pyaudio
import wave
from psychopy import core

PLAYING = 1
STOPPED = 2
FINISHED = 3

class PlaySound(object):
    """
    Asynchronously plays a wav file using PyAudio and the builtin wav module.
    See the end of file for a simple usage example.

    Uses audio stream buffer callback times to set the start and end time
    of the audio playback. Accuracy of these times is unknown right now.
    """
    _pya = None
    def __init__(self, filename=None):
        if PlaySound._pya is None:
            PlaySound._pya = pyaudio.PyAudio()

        self._filename = None
        self._starttime = None
        self._endtime = None

        self._stream = None
        self._wf = None

        if filename:
            self.setFile(filename)

    def setFile(self, filename):
        if self._filename:
            self.closeFile()
        self._starttime = None
        self._endtime = None
        self._filename = filename
        self._wf = wf = wave.open(self._filename, 'rb')
        self._stream = self._pya.open(format=self._pya.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=self.callback)
        self.bytes_per_sample = wf.getsampwidth()*wf.getnchannels()
        self.sampling_rate = wf.getframerate()

    def callback(self, in_data, frame_count, time_info, status):
        data = self._wf.readframes(frame_count)
        if self._starttime is None:
            self._starttime = core.getTime()
        chunk_dur = len(data)/self.bytes_per_sample/self.sampling_rate
        self._endtime = core.getTime()+chunk_dur
        return (data, pyaudio.paContinue)

    def start(self):
        if self._stream:
            self._stream.start_stream()

    def stop(self):
        if self._stream:
            self._stream.stop_stream()

    def closeFile(self):
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        if self._wf:
            self._wf.close()
            self._wf = None
        self._starttime = None
        self._endtime = None
        self.bytes_per_sample = None
        self.sampling_rate = None

    @property
    def starttime(self):
        return self._starttime

    @property
    def endtime(self):
        return self._endtime

    @property
    def status(self):
        if self._stream.is_active():
            return PLAYING
        if self._stream.is_stopped():
            return STOPPED
        if self._wf.tell()>=self._wf.getnframes():
            return FINISHED

    def __del__(self):
        self.closeFile()

if __name__ == '__main__':
    '''
    Simple test of the PlaySound class. afname variable should be changed to
    reference an existing .wav audio file path.
    '''
    import time, os
    afname = os.path.join(os.path.dirname(__file__),
                                        u'resources',u'audio',u'6-5.wav')
    s = PlaySound(filename=afname)
    
    s.start()

    while s.status == PLAYING:
        time.sleep(0.1)

    print("Audio start:",s.starttime)
    print("Audio end:",s.endtime)

    s.closeFile()
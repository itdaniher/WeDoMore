#!/usr/bin/env python
#Copyright (c) 2011 Walter Bender
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

try:
    from numpy import append
    from numpy.fft import rfft
    PITCH_AVAILABLE = True
except:
    PITCH_AVAILABLE = False

from gettext import gettext as _

from plugin import Plugin

from audio.audiograb import AudioGrab_Unknown, AudioGrab_XO1, AudioGrab_XO15, \
    SENSOR_DC_NO_BIAS, SENSOR_DC_BIAS

from audio.ringbuffer import RingBuffer1d

from TurtleArt.tapalette import make_palette
from TurtleArt.taconstants import XO1, XO15
from TurtleArt.talogo import primitive_dictionary

import logging
_logger = logging.getLogger('turtleart-activity audio sensors plugin')


def _avg(array, abs_value=False):
    """ Calc. the average value of an array """
    if len(array) == 0:
        return 0
    array_sum = 0
    if abs_value:
        for a in array:
            array_sum += abs(a)
    else:
        for a in array:
            array_sum += a
    return float(array_sum) / len(array)


class Audio_sensors_plugin(Plugin):

    def __init__(self, parent):
        self._parent = parent
        self.hw = self._parent.hw
        self.running_sugar = self._parent.running_sugar
        self._status = True  # TODO: test for audio device

    def setup(self):
        # set up audio-sensor-specific blocks
        if not self._status:
            return

        self.max_samples = 1500
        self.input_step = 1

        self.ringbuffer = RingBuffer1d(self.max_samples, dtype='int16')
        if self.hw == XO1:
            self.voltage_gain = 0.00002225
            self.voltage_bias = 1.140
        elif self.hw == XO15:
            self.voltage_gain = -0.0001471
            self.voltage_bias = 1.695

        palette = make_palette('sensor',
                               colors=["#FF6060", "#A06060"],
                               help_string=_('Palette of sensor blocks'))

        primitive_dictionary['sound'] = self.prim_sound
        palette.add_block('sound',
                          style='box-style',
                          label=_('sound'),
                          help_string=_('raw microphone input signal'),
                          value_block=True,
                          prim_name='sound')
        self._parent.lc.def_prim('sound', 0,
                                  lambda self: primitive_dictionary['sound']())

        primitive_dictionary['volume'] = self.prim_volume
        palette.add_block('volume',
                          style='box-style',
                          label=_('loudness'),
                          help_string=_('microphone input volume'),
                          value_block=True,
                          prim_name='volume')
        self._parent.lc.def_prim('volume', 0,
            lambda self: primitive_dictionary['volume']())

        primitive_dictionary['pitch'] = self.prim_pitch
        if PITCH_AVAILABLE:
            palette.add_block('pitch',
                              style='box-style',
                              label=_('pitch'),
                              help_string=_('microphone input pitch'),
                              value_block=True,
                              prim_name='pitch')
        else:
            palette.add_block('pitch',
                              hidden=True,
                              style='box-style',
                              label=_('pitch'),
                              help_string=_('microphone input pitch'),
                              value_block=True,
                              prim_name='pitch')
        self._parent.lc.def_prim('pitch', 0,
                                  lambda self: primitive_dictionary['pitch']())

        if self.hw in [XO1, XO15]:
            primitive_dictionary['resistance'] = self.prim_resistance
            palette.add_block('resistance',
                              style='box-style',
                              label=_('resistance'),
                              help_string=_('microphone input resistance'),
                              value_block=True,
                              prim_name='resistance')
            self._parent.lc.def_prim('resistance', 0,
                lambda self: primitive_dictionary['resistance']())

            primitive_dictionary['voltage'] = self.prim_voltage
            palette.add_block('voltage',
                              style='box-style',
                              label=_('voltage'),
                              help_string=_('microphone input voltage'),
                              value_block=True,
                              prim_name='voltage')
            self._parent.lc.def_prim('voltage', 0,
                lambda self: primitive_dictionary['voltage']())

        self.audio_started = False

    def start(self):
        # This gets called by the start button
        if not self._status:
            return
        """ Start grabbing audio if there is an audio block in use """
        if len(self._parent.block_list.get_similar_blocks('block',
            ['volume', 'sound', 'pitch', 'resistance', 'voltage'])) > 0:
            if self.audio_started:
                self.audiograb.resume_grabbing()
            else:
                if self.hw == XO15:
                    self.audiograb = AudioGrab_XO15(self.new_buffer, self)
                elif self.hw == XO1:
                    self.audiograb = AudioGrab_XO1(self.new_buffer, self)
                else:
                    self.audiograb = AudioGrab_Unknown(self.new_buffer, self)
                self.audiograb.start_grabbing()
                self.audio_started = True
        self._update_audio_mode()

    def new_buffer(self, buf):
        """ Append a new buffer to the ringbuffer """
        self.ringbuffer.append(buf)
        return True

    def _update_audio_mode(self):
        """ If there are sensor blocks, set the appropriate audio mode """
        if not hasattr(self._parent.lc, 'value_blocks'):
            return
        for name in ['sound', 'volume', 'pitch']:
            if name in self._parent.lc.value_blocks:
                if len(self._parent.lc.value_blocks[name]) > 0:
                    self.audiograb.set_sensor_type()
                    return
        if 'resistance' in self._parent.lc.value_blocks:
            if len(self._parent.lc.value_blocks['resistance']) > 0:
                self.audiograb.set_sensor_type(SENSOR_DC_BIAS)
                return
        if 'voltage' in self._parent.lc.value_blocks:
            if len(self._parent.lc.value_blocks['voltage']) > 0:
                self.audiograb.set_sensor_type(SENSOR_DC_NO_BIAS)
                return

    def stop(self):
        # This gets called by the stop button
        if self._status:
            if self.audio_started:
                self.audiograb.pause_grabbing()

    def goto_background(self):
        # This gets called when your process is sent to the background
        # TODO: handle this case
        pass

    def return_to_foreground(self):
        # This gets called when your process returns from the background
        # TODO: handle this case
        pass

    def quit(self):
        # This gets called by the quit button
        self.stop()

    def _status_report(self):
        print 'Reporting audio sensor status: %s' % (str(self._status))
        return self._status

    # Block primitives used in talogo

    def prim_volume(self):
        """ return mic in value """
        #TODO: Adjust gain for different HW
        buf = self.ringbuffer.read(None, self.input_step)
        if len(buf) > 0:
            volume = float(_avg(buf, abs_value=True))
            self._parent.lc.update_label_value('volume', volume)
            return volume
        else:
            return 0

    def prim_sound(self):
        """ return raw mic in value """
        buf = self.ringbuffer.read(None, self.input_step)
        if len(buf) > 0:
            sound = float(buf[0])
            self._parent.lc.update_label_value('sound', sound)
            return sound
        else:
            return 0

    def prim_pitch(self):
        """ return index of max value in fft of mic in values """
        if not PITCH_AVAILABLE:
            return 0
        buf = []
        for i in range(4):
            buf = append(buf, self.ringbuffer.read(None, self.input_step))
        if len(buf) > 0:
            r = []
            for j in rfft(buf):
                r.append(abs(j))
            # Convert output to Hertz
            pitch = r.index(max(r)) * 48000 / len(buf)
            self._parent.lc.update_label_value('pitch', pitch)
            return pitch
        else:
            return 0

    def prim_resistance(self):
        """ return resistance sensor value """
        buf = self.ringbuffer.read(None, self.input_step)
        if len(buf) > 0:
            # See <http://bugs.sugarlabs.org/ticket/552#comment:7>
            # TODO: test this calibration on XO 1.5
            if self.hw == XO1:
                resistance = 2.718 ** ((float(_avg(buf)) * 0.000045788) + \
                                           8.0531)
            else:
                avg_buf = float(_avg(buf))
                if avg_buf > 0:
                    resistance = (420000000 / avg_buf) - 13500
                else:
                    resistance = 420000000
            self._parent.lc.update_label_value('resistance', resistance)
            return resistance
        else:
            return 0

    def prim_voltage(self):
        """ return voltage sensor value """
        buf = self.ringbuffer.read(None, self.input_step)
        if len(buf) > 0:
            # See <http://bugs.sugarlabs.org/ticket/552#comment:7>
            voltage = float(_avg(buf)) * self.voltage_gain + self.voltage_bias
            self._parent.lc.update_label_value('voltage', voltage)
            return voltage
        else:
            return 0

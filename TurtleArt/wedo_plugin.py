#!/usr/bin/env python

from plugin import Plugin

from TurtleArt.tapalette import make_palette
from TurtleArt.taconstants import XO1, XO15
from TurtleArt.talogo import primitive_dictionary

import logging
_logger = logging.getLogger('turtleart-activity Lego WeDo plugin')


class WeDo_plugin(Plugin):

	def __init__(self, parent):
	    self._parent = parent
	    self.hw = self._parent.hw
	    self.running_sugar = self._parent.running_sugar
	    self._status = True

	def setup(self):
	    # set up audio-sensor-specific blocks
	    if not self._status:
	        return

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

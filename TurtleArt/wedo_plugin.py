from gettext import gettext as _

from plugin import Plugin
from plugins.lib.WeDoMore import WeDo

from TurtleArt.tapalette import make_palette
from TurtleArt.taconstants import XO1, XO15
from TurtleArt.talogo import primitive_dictionary

import logging
_logger = logging.getLogger('turtleart-activity WeDo plugin')


class Wedo_plugin(Plugin):

	def __init__(self, parent):
		self.WeDo = WeDo()
		self._parent = parent
	def setup(self):

		palette = make_palette('WeDo', colors=["#FF6060", "#A06060"], help_string=_('Palette of WeDo blocks'))

		primitive_dictionary['tilt'] = self.WeDo.getTilt

		palette.add_block('tilt',
						style='box-style',
						label=_('tilt'),
						help_string=_('tilt sensor output'),
						value_block=True,
						prim_name = 'tilt')

		self._parent.lc.def_prim('tilt', 0, lambda self: primitive_dictionary['tilt']())

		primitive_dictionary['distance'] = self.WeDo.getDistance

		palette.add_block('distance',
						style='box-style',
						label=_('distance'),
						help_string=_('distance sensor output'),
						value_block=True,
						prim_name = 'distance')

		self._parent.lc.def_prim('distance', 0, lambda self: primitive_dictionary['distance']())
		
		primitive_dictionary['getMotorA'] = self.WeDo.getMotorA

		palette.add_block('getMotorA',
						style='box-style',
						label=_('Motor A Value'),
						help_string=_('returns the current value of Motor A'),
						value_block=True,
						prim_name = 'getMotorA')

		self._parent.lc.def_prim('getMOtorA', 0, lambda self: primitive_dictionary['getMotorA']())

		primitive_dictionary['getMotorB'] = self.WeDo.getMotorA

		palette.add_block('getMotorB',
						style='box-style',
						label=_('Motor B Value'),
						help_string=_('returns the current value of Motor B'),
						value_block=True,
						prim_name = 'getMotorB')

		self._parent.lc.def_prim('getMOtorB', 0, lambda self: primitive_dictionary['getMotorB']())

		primitive_dictionary['setMotorA'] = self.WeDo.setMotorA

		palette.add_block('setMotorA',
						style = 'basic-style-1arg',
						label = _('setMotorA'),
						default = ['a'],
						prim_name = 'setMotorA',
						help_string = _(''))

		self._parent.lc.def_prim('setMotorA', 1,
                                  lambda self, a: primitive_dictionary['setMotorA'](a))

		primitive_dictionary['setMotorB'] = self.WeDo.setMotorB

		palette.add_block('setMotorB',
						style = 'basic-style-1arg',
						label = _('setMotorB'),
						default = ['b'],
						prim_name = 'setMotorB',
						help_string = _(''))

		self._parent.lc.def_prim('setMotorB', 1,
                                  lambda self, b: primitive_dictionary['setMotorB'](b))

	def start(self):
		pass

	def stop(self):
	    self.WeDo.setMotors(0,0)

	def goto_background(self):
	    pass

	def return_to_foreground(self):
	    pass

	def quit(self):
		self.WeDo.setMotors(0,0)

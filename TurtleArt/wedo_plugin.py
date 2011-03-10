from gettext import gettext as _

from plugin import Plugin
from WeDoMore import WeDo

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

		palette.add_block('distance',
						style='box-style',
						label=_('distance'),
						help_string=_('distance sensor output'),
						value_block=True,
						prim_name = 'distance')

		self._parent.lc.def_prim('distance', 0, lambda self: primitive_dictionary['distance']())

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

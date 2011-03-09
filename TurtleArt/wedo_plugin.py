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

		palette = make_palette('sensor', colors=["#FF6060", "#A06060"], help_string=_('Palette of sensor blocks'))

		primitive_dictionary['distance'] = self.prim_distance

		palette.add_block('distance',
						style='box-style',
						label=_('distance'),
						help_string=_('distance sensor output'),
						value_block=True,
						prim_name = 'distance')

		self._parent.lc.def_prim('distance', 0,
                                  lambda self: primitive_dictionary['distance']())

	def prim_distance(self):
		self.WeDo.getDistance()

	def start(self):
		pass

	def stop(self):
		pass

	def goto_background(self):
	    pass

	def return_to_foreground(self):
	    pass

	def quit(self):
	    self.stop()

	def prim_distance(self):
		return self.WeDo.getDistance()


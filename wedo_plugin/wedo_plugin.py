from gettext import gettext as _

from plugins.plugin import Plugin

import os
import sys
sys.path.insert(0, os.path.abspath('./plugins/wedo_plugin'))

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
        if self.WeDo.dev is None:
            self._status = False  # no WeDo device found
        else:
            self._status = True

    def setup(self):

        palette = make_palette('WeDo', colors=["#FF6060", "#A06060"],
			       help_string=_('Palette of WeDo blocks'))

        primitive_dictionary['wedotilt'] = self.WeDo.getTilt
        palette.add_block('tilt',
                        style='box-style',
                        label=_('tilt'),
                        help_string=_('tilt sensor output: (-1 == no tilt,\
 0 == tilt forward, 3 == tilt back, 1 == tilt left, 2 == tilt right)'),
                        value_block=True,
                        prim_name = 'wedotilt')
        self._parent.lc.def_prim(
            'wedotilt', 0, lambda self: primitive_dictionary['wedotilt']())

        primitive_dictionary['wedodistance'] = self.WeDo.getDistance
        palette.add_block('wedodistance',
                        style='box-style',
                        label=_('distance'),
                        help_string=_('distance sensor output'),
                        value_block=True,
                        prim_name = 'wedodistance')
        self._parent.lc.def_prim(
            'wedodistance', 0,
            lambda self: primitive_dictionary['wedodistance']())
        
        primitive_dictionary['wedogetMotorA'] = self.WeDo.getMotorA
        palette.add_block('wedogetMotorA',
                        style='box-style',
                        label=_('Motor A'),
                        help_string=_('returns the current value of Motor A'),
                        value_block=True,
                        prim_name = 'wedogetMotorA')

        self._parent.lc.def_prim('wedogetMotorA', 0,
				 lambda self: primitive_dictionary['wedogetMotorA']())

        primitive_dictionary['wedogetMotorB'] = self.WeDo.getMotorB
        palette.add_block('wedogetMotorB',
                        style='box-style',
                        label=_('Motor B'),
                        help_string=_('returns the current value of Motor B'),
                        value_block=True,
                        prim_name = 'wedogetMotorB')
        self._parent.lc.def_prim(
            'wedogetMotorB', 0,
            lambda self: primitive_dictionary['wedogetMotorB']())

        primitive_dictionary['wedosetMotorA'] = self.WeDo.setMotorA
        palette.add_block('wedosetMotorA',
                        style = 'basic-style-1arg',
                        label = _('Motor A'),
                        default = 0,
                        prim_name = 'wedosetMotorA',
                        help_string = _('set the value for Motor A'))
        self._parent.lc.def_prim(
            'wedosetMotorA', 1,
            lambda self, a: primitive_dictionary['wedosetMotorA'](a))

        primitive_dictionary['wedosetMotorB'] = self.WeDo.setMotorB
        palette.add_block('wedosetMotorB',
                        style = 'basic-style-1arg',
                        label = _('Motor B'),
                        default = 0,
                        prim_name = 'wedosetMotorB',
                        help_string = _('set the value for Motor B'))
        self._parent.lc.def_prim(
            'wedosetMotorB', 1,
            lambda self, b: primitive_dictionary['wedosetMotorB'](b))

    def start(self):
        pass

    def stop(self):
        if self._status:
            self.WeDo.setMotors(0, 0)

    def goto_background(self):
        pass

    def return_to_foreground(self):
        pass

    def quit(self):
        if self._status:
            self.WeDo.setMotors(0, 0)

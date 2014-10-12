#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011, 2012 Ian Daniher
# Copyright (c) 2012 Tony Forster, Walter Bender, Alan Aguiar
# Copyright (c) 2013 Alan Aguiar
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

import os
import sys
sys.path.insert(0, os.path.abspath('./plugins/wedo_plugin'))
from TurtleArt.tapalette import make_palette
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_blocks
from TurtleArt.talogo import logoerror
from TurtleArt.taprimitive import Primitive, ArgSlot
from TurtleArt.tatype import TYPE_INT, TYPE_NUMBER
from plugins.plugin import Plugin
from wedo import WeDo, scan_for_devices, UNAVAILABLE
from gettext import gettext as _

COLOR_NOTPRESENT = ["#A0A0A0","#808080"]
COLOR_PRESENT = ["#FF6060", "#A06060"]
ERROR_NO_NUMBER = _("The parameter must be a integer, not '%s'")
ERROR_SPEED = _('Motor speed must be an integer between -100 and 100')
WEDO_FOUND = _('WeDo found %s bricks')
WEDO_NOT_FOUND = _('WeDo not found')
INDEX_NOT_FOUND = _('WeDo number %s was not found')
ERROR = -1


class Wedo_plugin(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self)
        self.tw = parent
        self.WeDos = []
        self.active_wedo = 0

    def setup(self):

        palette = make_palette('wedo', COLOR_NOTPRESENT, _('Palette of WeDo blocks'),
                                translation=_('wedo'))

        palette.add_block('wedorefresh',
                style='basic-style',
                label=_('refresh WeDo'),
                prim_name='wedorefresh',
                help_string=_('Search for a connected WeDo.'))
        self.tw.lc.def_prim('wedorefresh', 0,
            Primitive(self.refresh))
        special_block_colors['wedorefresh'] = COLOR_PRESENT[:]

        palette.add_block('wedoselect',
                style='basic-style-1arg',
                default = 1,
                label=_('WeDo'),
                help_string=_('set current WeDo device'),
                prim_name = 'wedoselect')
        self.tw.lc.def_prim('wedoselect', 1,
            Primitive(self.select, arg_descs=[ArgSlot(TYPE_NUMBER)]))

        palette.add_block('wedogetcount',
                style='box-style',
                label=_('number of WeDos'),
                help_string=_('number of WeDo devices'),
                prim_name = 'wedocount')
        self.tw.lc.def_prim('wedocount', 0,
            Primitive(self.count, TYPE_INT))

        palette.add_block('tilt',
                style='box-style',
                label=_('tilt'),
                help_string=_('tilt sensor output: (-1 == no tilt,\
0 == tilt forward, 3 == tilt back, 1 == tilt left, 2 == tilt right)'),
                value_block=True,
                prim_name = 'wedotilt')
        self.tw.lc.def_prim('wedotilt', 0,
            Primitive(self.getTilt, TYPE_INT))

        palette.add_block('wedodistance',
                style='box-style',
                label=_('distance'),
                help_string=_('distance sensor output'),
                value_block=True,
                prim_name = 'wedodistance')
        self.tw.lc.def_prim('wedodistance', 0,
            Primitive(self.getDistance, TYPE_INT))
        
        palette.add_block('wedogetMotorA',
                style='box-style',
                label=_('Motor A'),
                help_string=_('returns the current speed of Motor A'),
                value_block=True,
                prim_name = 'wedogetMotorA')
        self.tw.lc.def_prim('wedogetMotorA', 0,
            Primitive(self.getMotorA, TYPE_INT))

        palette.add_block('wedogetMotorB',
                style='box-style',
                label=_('Motor B'),
                help_string=_('returns the current speed of Motor B'),
                value_block=True,
                prim_name = 'wedogetMotorB')
        self.tw.lc.def_prim('wedogetMotorB', 0,
            Primitive(self.getMotorB, TYPE_INT))

        palette.add_block('wedosetMotorA',
                style = 'basic-style-1arg',
                label = _('Motor A'),
                default = 30,
                prim_name = 'wedosetMotorA',
                help_string = _('set the speed for Motor A'))
        self.tw.lc.def_prim('wedosetMotorA', 1,
            Primitive(self.setMotorA, arg_descs=[ArgSlot(TYPE_NUMBER)]))

        palette.add_block('wedosetMotorB',
                style = 'basic-style-1arg',
                label = _('Motor B'),
                default = 30,
                prim_name = 'wedosetMotorB',
                help_string = _('set the speed for Motor B'))
        self.tw.lc.def_prim('wedosetMotorB', 1,
            Primitive(self.setMotorB, arg_descs=[ArgSlot(TYPE_NUMBER)]))

    ############################### Turtle signals ############################

    def stop(self):
        self.stop_all()

    def quit(self):
        self.stop_all()

    ################################# Primitives ##############################

    def refresh(self):
        self.wedo_find()
        self.change_color_blocks()
        if self.WeDos:
            n = self.count()
            self.tw.showlabel('print', WEDO_FOUND % int(n))
        else:
            self.tw.showlabel('print', WEDO_NOT_FOUND)

    def select(self, i):
        ''' Select current device '''
        if self.count() == 0:
            raise logoerror(WEDO_NOT_FOUND)
        try:
            t = int(i)
            t = t - 1
        except:
            raise logoerror(ERROR_NO_NUMBER % i)
        if (t < self.count()) and (t >= 0):
            self.active_wedo = t
        else:
            raise logoerror(INDEX_NOT_FOUND % (t + 1))

    def count(self):
        ''' How many devices are available? '''
        return len(self.WeDos)

    def getTilt(self):
        if self.WeDos:
            wedo = self.WeDos[self.active_wedo]
            if wedo.tilt == UNAVAILABLE:
                return ERROR
            return wedo.tilt
        else:
            return ERROR

    def getDistance(self):
        if self.WeDos:
            wedo = self.WeDos[self.active_wedo]
            if wedo.distance == UNAVAILABLE:
                return ERROR
            return wedo.distance
        else:
            return ERROR

    def getMotorA(self):
        if self.WeDos:
            wedo = self.WeDos[self.active_wedo]
            return wedo.motor_a
        else:
            return ERROR

    def getMotorB(self):
        if self.WeDos:
            wedo = self.WeDos[self.active_wedo]
            return wedo.motor_b
        else:
            return ERROR

    def setMotorA(self, speed):
        try:
            speed = int(speed)
        except:
            raise logoerror(ERROR_SPEED)
        if speed > 100 or speed < -100:
            raise logoerror(ERROR_SPEED)
        if self.WeDos:
            wedo = self.WeDos[self.active_wedo]
            wedo.motor_a = speed

    def setMotorB(self, speed):
        try:
            speed = int(speed)
        except:
            raise logoerror(ERROR_SPEED)
        if speed > 100 or speed < -100:
            raise logoerror(ERROR_SPEED)
        if self.WeDos:
            wedo = self.WeDos[self.active_wedo]
            wedo.motor_b = speed

    ############################### Useful functions ##########################

    def wedo_find(self):
        for wedo in self.WeDos:
            wedo.dev = None
        self.WeDos = []
        self.active_wedo = 0
        for dev in scan_for_devices():
            w = WeDo(dev)
            self.WeDos.append(w)

    def stop_all(self):
        for wedo in self.WeDos:
            wedo.motor_a = 0
            wedo.motor_b = 0

    def change_color_blocks(self):
        index = palette_name_to_index('wedo')
        if (index is not None):
            wedo_blocks = palette_blocks[index]
            for block in self.tw.block_list.list:
                if block.type in ['proto', 'block']:
                    if block.name in wedo_blocks:
                        if (self.WeDos) or (block.name == 'wedorefresh'):
                            special_block_colors[block.name] = COLOR_PRESENT[:]
                        else:
                            special_block_colors[block.name] = COLOR_NOTPRESENT[:]
                        block.refresh()
            self.tw.regenerate_palette(index)


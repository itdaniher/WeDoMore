#Copyright (c) 2012, Tony Forster, Ian Daniher, Walter Bender
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

from gettext import gettext as _

from plugins.plugin import Plugin
from WeDoMore import WeDo, scan_for_devices, UNAVAILABLE

from TurtleArt.tapalette import make_palette
from TurtleArt.taconstants import XO1, XO15
from TurtleArt.talogo import primitive_dictionary

import logging
_logger = logging.getLogger('turtleart-activity WeDo plugin')


class Wedo_plugin(Plugin):

    def __init__(self, parent):
        ''' Scan for WeDo devices '''
        self.WeDos = []
        device_list = scan_for_devices()
        for i, dev in enumerate(device_list):
            self.WeDos.append(WeDo(device=dev))
            self.WeDos[-1].number = i
        self._parent = parent
        if len(self.WeDos) == 0:
            self._status = False  # no WeDo devices found
            self.active_wedo = None
        else:
            self._status = True
            self.active_wedo = 0

    def setup(self):
        ''' Setup palettes '''
        palette = make_palette('WeDo', colors=["#FF6060", "#A06060"],
			       help_string=_('Palette of WeDo blocks'))

        primitive_dictionary['wedoselect'] = self.wedo_select
        palette.add_block('wedoselect',
                          style='basic-style-1arg',
                          default = 1,
                          label=_('WeDo'),
                          help_string=_('set current WeDo device'),
                          prim_name = 'wedoselect')

        self._parent.lc.def_prim(
            'wedoselect', 1,
            lambda self, n: primitive_dictionary['wedoselect'](n))

        primitive_dictionary['wedocount'] = self.wedo_count
        palette.add_block('wedogetcount',
                          style='box-style',
                          label=_('number of WeDos'),
                          help_string=_('number of WeDo devices'),
                          prim_name = 'wedocount')

        self._parent.lc.def_prim(
            'wedocount', 0, lambda self: primitive_dictionary['wedocount']())

        primitive_dictionary['wedotilt'] = self.wedo_gettilt
        palette.add_block('tilt',
                        style='box-style',
                        label=_('tilt'),
                        help_string=_('tilt sensor output: (-1 == no tilt,\
 0 == tilt forward, 3 == tilt back, 1 == tilt left, 2 == tilt right)'),
                        value_block=True,
                        prim_name = 'wedotilt')
        self._parent.lc.def_prim(
            'wedotilt', 0, lambda self: primitive_dictionary['wedotilt']())

        primitive_dictionary['wedodistance'] = self.wedo_getdistance
        palette.add_block('wedodistance',
                        style='box-style',
                        label=_('distance'),
                        help_string=_('distance sensor output'),
                        value_block=True,
                        prim_name = 'wedodistance')
        self._parent.lc.def_prim(
            'wedodistance', 0,
            lambda self: primitive_dictionary['wedodistance']())
        
        primitive_dictionary['wedogetMotorA'] = self.wedo_getmotora
        palette.add_block('wedogetMotorA',
                        style='box-style',
                        label=_('Motor A'),
                        help_string=_('returns the current value of Motor A'),
                        value_block=True,
                        prim_name = 'wedogetMotorA')

        self._parent.lc.def_prim(
            'wedogetMotorA', 0,
            lambda self: primitive_dictionary['wedogetMotorA']())

        primitive_dictionary['wedogetMotorB'] = self.wedo_getmotorb
        palette.add_block('wedogetMotorB',
                        style='box-style',
                        label=_('Motor B'),
                        help_string=_('returns the current value of Motor B'),
                        value_block=True,
                        prim_name = 'wedogetMotorB')
        self._parent.lc.def_prim(
            'wedogetMotorB', 0,
            lambda self: primitive_dictionary['wedogetMotorB']())

        primitive_dictionary['wedosetMotorA'] = self.wedo_setmotora
        palette.add_block('wedosetMotorA',
                        style = 'basic-style-1arg',
                        label = _('Motor A'),
                        default = 30,
                        prim_name = 'wedosetMotorA',
                        help_string = _('set the value for Motor A'))
        self._parent.lc.def_prim(
            'wedosetMotorA', 1,
            lambda self, a: primitive_dictionary['wedosetMotorA'](a))

        primitive_dictionary['wedosetMotorB'] = self.wedo_setmotorb
        palette.add_block('wedosetMotorB',
                        style = 'basic-style-1arg',
                        label = _('Motor B'),
                        default = 30,
                        prim_name = 'wedosetMotorB',
                        help_string = _('set the value for Motor B'))
        self._parent.lc.def_prim(
            'wedosetMotorB', 1,
            lambda self, b: primitive_dictionary['wedosetMotorB'](b))

    def wedo_select(self, i):
        ''' Select current device '''
        if type(i) == unicode:
            i = str(i.encode('ascii', 'replace'))
        if type(i) == float or type(i) == str:
            i = int(i)
        if type(i) != int:
            i = 1
        i -= 1  # Userspace counts from 1; internally, we count from 0
        if i < 0 or i > self.wedo_count() - 1:
            self._parent.showlabel(
                'status', _('WeDo %d is not available; defaulting to 1') % (i))
        if i < 0:
            i = -i
        if i > self.wedo_count() - 1:
            i = 0
        self.active_wedo = i

    def wedo_count(self):
        ''' How many devices are available? '''
        n = len(self.WeDos)
        for wedo in self.WeDos:
            if wedo.dev is None:
                n -= 1
        return n

    def wedo_find(self):
        ''' Find an available device '''
        for wedo in self.WeDos:
            if wedo.dev is not None:
                return self.WeDos.index(wedo)
        return None

    def wedo_gettilt(self):
        if self.active_wedo is None:
            self.active_wedo = self.wedo_find()
            if self.active_wedo is None:
                self._parent.showlabel('status', _('WeDo is unavailable'))
                return -1
        tilt = self.WeDos[self.active_wedo].getTilt()
        if tilt == UNAVAILABLE:
            # Should we look for tilt on another WeDo?
            self._parent.showlabel(
                'status', _('%s is unavailable on WeDo %d') % (
                    _('tilt'), self.active_wedo + 1))
            return -1
        else:
            return tilt

    def wedo_getdistance(self):
        if self.active_wedo is None:
            self.active_wedo = self.wedo_find()
            if self.active_wedo is None:
                self._parent.showlabel('status', _('WeDo is unavailable'))
                return 0
        distance = self.WeDos[self.active_wedo].getDistance()
        if distance == UNAVAILABLE:
            # Should we look for distance on another WeDo?
            self._parent.showlabel(
                'status', _('%s is unavailable on WeDo %d') % (
                    _('distance'), self.active_wedo + 1))
            return 0
        else:
            return distance

    def wedo_getmotora(self):
        if self.active_wedo is None:
            self.active_wedo = self.wedo_find()
            if self.active_wedo is None:
                self._parent.showlabel('status', _('WeDo is unavailable'))
                return 0
        speed = self.WeDos[self.active_wedo].getMotorA()
        if speed == UNAVAILABLE:
            self._parent.showlabel(
                'status', _('%s is unavailable on WeDo %d') % (
                    _('Motor A'), self.active_wedo + 1))
            return 0
        else:
            return speed

    def wedo_getmotorb(self):
        if self.active_wedo is None:
            self.active_wedo = self.wedo_find()
            if self.active_wedo is None:
                self._parent.showlabel('status', _('WeDo is unavailable'))
                return 0
        speed = self.WeDos[self.active_wedo].getMotorB()
        if speed == UNAVAILABLE:
            self._parent.showlabel(
                'status', _('%s is unavailable on WeDo %d') % (
                    _('Motor B'), self.active_wedo + 1))
            return 0
        else:
            return speed

    def wedo_setmotora(self, speed):
        if self.active_wedo is None:
            self.active_wedo = self.wedo_find()
        if self.active_wedo is None:
            self._parent.showlabel('status', _('WeDo is unavailable'))
            return
        status = self.WeDos[self.active_wedo].setMotorA(speed)
        if status == UNAVAILABLE:
            self._parent.showlabel(
                'status', _('%s is unavailable on WeDo %d') % (
                    _('Motor A'), self.active_wedo + 1))

    def wedo_setmotorb(self, speed):
        if self.active_wedo is None:
            self.active_wedo = self.wedo_find()
        if self.active_wedo is None:
            self._parent.showlabel('status', _('WeDo is unavailable'))
            return
        status = self.WeDos[self.active_wedo].setMotorB(speed)
        if status == UNAVAILABLE:
            self._parent.showlabel(
                'status', _('%s is unavailable on WeDo %d') % (
                    _('Motor B'), self.active_wedo + 1))

    def start(self):
        ''' Each time program starts, scan for devices and reset status '''
        for wedo in self.WeDos:
            wedo.dev = None
        device_list = scan_for_devices()
        if len(device_list) > 0:
            self.status = True
            if self.active_wedo is None:
                self.active_wedo = 0
        else:
            self.status = False
        for i, dev in enumerate(device_list):
            if i < len(self.WeDos):
                self.WeDos[i].dev = dev
                self.WeDos[i].number = i
                self.WeDos[i].init_device()  # Reinitial device
            else:
                self.WeDos.append(WeDo(device=dev))
                self.WeDos[i].number = i

    def stop(self):
        if self._status:
            for wedo in self.WeDos:
                if wedo.dev is not None:
                    wedo.setMotors(0, 0)

    def goto_background(self):
        pass

    def return_to_foreground(self):
        pass

    def quit(self):
        if self._status:
            for wedo in self.WeDos:
                if wedo.dev is not None:
                    wedo.setMotors(0, 0)

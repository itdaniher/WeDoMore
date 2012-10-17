#Copyright (c) 2011, 2012, Ian Daniher
#Copyright (c) 2012, Tony Forster, Walter Bender
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

import sys
import os
sys.path.append(os.path.dirname(__file__))
import usb.core

import logging
logger = logging.getLogger('WeDoMore')


UNAVAILABLE = None
TILTSENSOR = [38, 39]
DISTANCESENSOR = [176, 177, 178, 179]
MOTOR = [0, 1, 2, 3, 238, 239]
TILT_FORWARD = 0
TILT_LEFT = 1
TILT_RIGHT = 2
TILT_BACK = 3
NO_TILT = -1


def scan_for_devices():
    ''' Find all available devices '''
    return usb.core.find(find_all=True, idVendor=0x0694, idProduct=0x0003)


class WeDo:
    def __init__(self, device=None):
        """Find a USB device with the VID and PID of the Lego
        WeDo. If the HID kernel driver is active, detatch
        it."""
        self.dev = None
        self.number = 0
        self.dev = device
        if self.dev is None:
            logging.debug("No Lego WeDo found")
        else:
            self.init_device()
        self.valMotorA = 0
        self.valMotorB = 0

    def init_device(self):
        ''' Reinit device associated with the WeDo instance '''
        if self.dev is not None:
            try:
                if self.dev.is_kernel_driver_active(0):
                    try:
                        self.dev.detach_kernel_driver(0)
                    except usb.core.USBError as e:
                        logger.error(
                            "Could not detatch kernel driver: %s" % (str(e)))
            except usb.core.USBError as e:
                logger.error("Could not talk to WeDo device: %s" % (str(e)))
        self.endpoint = self.dev[0][(0,0)][0]

    def getRawData(self):
        """Read 64 bytes from the WeDo's endpoint, but only
        return the last eight."""
        try:
            data = list(self.endpoint.read(64)[-8:])
        except usb.core.USBError as e:
            logger.error("Could not read from WeDo device: %s" % (str(e)))
            return None
        return data

    def processMotorValues(self, value):
        """Check to make sure motor values are sane."""
        retValue = int(value)
        if 0 < value < 101:
            retValue += 27 
        elif -101 < value < 0:
            retValue -= 27
        elif value == 0:
            retValue = 0
        return retValue
    
    def setMotors(self, valMotorA, valMotorB):
        """Arguments should be in form of a number between 0
        and 100, positive or negative. Magic numbers used for
        the ctrl_transfer derived from sniffing USB coms."""
        if self.dev is None:
            return
        self.valMotorA = self.processMotorValues(valMotorA)
        self.valMotorB = self.processMotorValues(valMotorB)
        data = [64, self.valMotorA&0xFF, self.valMotorB&0xFF,
                0x00, 0x00, 0x00, 0x00, 0x00]
        try:
            self.dev.ctrl_transfer(bmRequestType = 0x21, bRequest = 0x09,
                                   wValue = 0x0200, wIndex = 0,
                                   data_or_wLength = data)
        except usb.core.USBError as e:
            logger.error("Could not write to driver: %s" % (str(e)))

    def getData(self):
        """Sensor data is contained in the 2nd and 4th byte, with
        sensor IDs being contained in the 3rd and 5th byte
        respectively."""
        rawData = self.getRawData()
        if rawData is not None:
            sensorData = {rawData[3]: rawData[2], rawData[5]: rawData[4]}
        else:
            sensorData = {}
        return sensorData

    def processTilt(self, v):
        """Use a series of elif/value-checks to process the tilt
        sensor data."""
        if v in range(10, 40):
            return TILT_BACK
        elif v in range(60, 90):
            return TILT_RIGHT
        elif v in range(170, 190):
            return TILT_FORWARD
        elif v in range(220, 240):
            return TILT_LEFT
        elif v in range(120, 140):
            return NO_TILT
        else:
            return NO_TILT

    def getTilt(self):
        if self.dev is None:
            return UNAVAILABLE
        data = self.getData()
        for num in data.keys():
            if num in TILTSENSOR:
                return self.processTilt(data[num])
        return UNAVAILABLE

    def getDistance(self):
        if self.dev is None:
            return UNAVAILABLE
        data = self.getData()
        for num in data.keys():
            if num in DISTANCESENSOR:
                return data[num] - 69
        return UNAVAILABLE

    # TODO: check motor availability

    def setMotorA(self, valMotorA):
        self.setMotors(valMotorA, self.valMotorB)
        return self.valMotorA

    def setMotorB(self, valMotorB):
        self.setMotors(self.valMotorA, valMotorB)
        return self.valMotorB

    def getMotorA(self):
        if self.dev is None:
            return UNAVAILABLE
        if self.valMotorA == 0:
            return 0
        elif self.valMotorA < 0:
            return self.valMotorA + 27
        else:
            return self.valMotorA - 27

    def getMotorB(self):
        if self.dev is None:
            return UNAVAILABLE
        if self.valMotorB == 0:
            return 0
        elif self.valMotorB < 0:
            return self.valMotorB + 27
        else:
            return self.valMotorB - 27

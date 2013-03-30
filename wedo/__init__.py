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
from functools import wraps

import sys
import os

sys.path.append(os.path.dirname(__file__))
import usb.core

import logging

logger = logging.getLogger('WeDoMore')

ID_VENDOR, ID_PRODUCT = 0x0694, 0x0003
UNAVAILABLE = None
TILTSENSOR = [38, 39]
DISTANCESENSOR = [176, 177, 178, 179]
MOTOR = [0, 1, 2, 3, 238, 239]
TILT_FORWARD = 0
TILT_LEFT = 1
TILT_RIGHT = 2
TILT_BACK = 3
NO_TILT = -1


def device_required(f):
    """ A simple decorator to protect the instances with non working devices.
    """
    @wraps(f)
    def wrapper(*args, **kwds):
        if args[0].dev is None:
            raise ValueError("No device attached to this instance")
        return f(*args, **kwds)
    return wrapper

def scan_for_devices():
    """ Find all available devices """
    return usb.core.find(find_all=True, idVendor=ID_VENDOR, idProduct=ID_PRODUCT)


def processMotorValues(value):
    """Check to make sure motor values are sane."""
    if 0 < value <= 100:
        return value + 27
    elif -100 <= value < 0:
        return value - 27
    return 0


class WeDo:
    def __init__(self, device=None):
        """Find a USB device with the VID and PID of the Lego
        WeDo. If the HID kernel driver is active, detatch
        it."""
        self.number = 0
        self.dev = device
        if self.dev is None:
            devices = scan_for_devices()
            if not devices:
                raise OSError("Could not find a connected WeDo device")
            self.dev = devices[0]
        self.init_device()
        self.valMotorA = 0
        self.valMotorB = 0

    def init_device(self):
        """ Reinit device associated with the WeDo instance """
        if self.dev is None:
            raise ValueError("No device attached to this instance")
        try:
            if self.dev.is_kernel_driver_active(0):
                try:
                    self.dev.detach_kernel_driver(0)
                except usb.core.USBError as e:
                    logger.error(
                        "Could not detatch kernel driver: %s" % (str(e)))
            self.endpoint = self.dev[0][(0, 0)][0]
        except usb.core.USBError as e:
            logger.error("Could not talk to WeDo device: %s" % (str(e)))

    @device_required
    def getRawData(self):
        """Read 64 bytes from the WeDo's endpoint, but only
        return the last eight."""
        try:
            return self.endpoint.read(64)[-8:]
        except usb.core.USBError as e:
            logger.exception("Could not read from WeDo device")
        return None

    @device_required
    def setMotors(self):
        """Arguments should be in form of a number between 0
        and 100, positive or negative. Magic numbers used for
        the ctrl_transfer derived from sniffing USB coms."""
        data = [64, processMotorValues(self.valMotorA) & 0xFF, processMotorValues(self.valMotorB) & 0xFF,
                0x00, 0x00, 0x00, 0x00, 0x00]
        try:
            self.dev.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue=0x0200, wIndex=0, data_or_wLength=data)
        except usb.core.USBError as e:
            logger.exception("Could not write to driver")

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
        return NO_TILT

    @device_required
    def getTilt(self):
        data = self.getData()
        for num in data.keys():
            if num in TILTSENSOR:
                return self.processTilt(data[num])
        return UNAVAILABLE

    @device_required
    def getDistance(self):
        data = self.getData()
        for num in data.keys():
            if num in DISTANCESENSOR:
                return data[num] - 69
        return UNAVAILABLE

    def setMotorA(self, valMotorA):
        if valMotorA > 100 or valMotorA < -100:
            raise ValueError("A motor can only be between -100 and 100")
        self.valMotorA = valMotorA
        self.setMotors()
        return self.valMotorA

    def setMotorB(self, valMotorB):
        if valMotorB > 100 or valMotorB < -100:
            raise ValueError("A motor can only be between -100 and 100")
        self.valMotorB = valMotorB
        self.setMotors()
        return self.valMotorB

    def getMotorA(self):
        return self.valMotorA

    def getMotorB(self):
        return self.valMotorB

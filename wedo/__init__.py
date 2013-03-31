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

from wedo.distance import interpolate_distance_data
from wedo.tilt import process_tilt
import usb.core
import logging

logger = logging.getLogger('WeDoMore')

ID_VENDOR, ID_PRODUCT = 0x0694, 0x0003
UNAVAILABLE = None
TILTSENSOR = (38, 39)
DISTANCESENSOR = (176, 177, 178, 179)
MOTOR = (0, 1, 2, 3, 238, 239)


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


class WeDo(object):

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

    @property
    @device_required
    def raw_tilt(self):
        """
        Returns the raw tilt direction (arbitrary units)
        """
        data = self.getData()
        for num in data:
            if num in TILTSENSOR:
                return data[num]
        return UNAVAILABLE

    @property
    @device_required
    def tilt(self):
        """
        Returns the tilt direction (one of the FLAT, TILT_FORWARD, TILT_LEFT, TILT_RIGHT, TILT_BACK constants)
        """
        raw_data = self.raw_tilt
        if raw_data is UNAVAILABLE:
            return UNAVAILABLE
        return process_tilt(raw_data)

    @property
    @device_required
    def raw_distance(self):
        """
        Return the raw evaluated distance from the distance meter (arbitrary units)
        """
        data = self.getData()
        for num in data:
            if num in DISTANCESENSOR:
                return data[num]
        return UNAVAILABLE

    @property
    @device_required
    def distance(self):
        """
        Return the evaluated distance in meters from the distance meter.
        (Note: this is the ideal distance without any objets on the side, you might have to adapt it depending on your construction)
        """

        raw_data = self.raw_distance
        if raw_data is UNAVAILABLE:
            return UNAVAILABLE
        return interpolate_distance_data(raw_data)

    @property
    def motor_a(self):
        return self.valMotorA

    @property
    def motor_b(self):
        return self.valMotorB

    @motor_a.setter
    def motor_a(self, valMotorA):
        if valMotorA > 100 or valMotorA < -100:
            raise ValueError("A motor can only be between -100 and 100")
        self.valMotorA = valMotorA
        self.setMotors()

    @motor_b.setter
    def motor_b(self, valMotorB):
        if valMotorB > 100 or valMotorB < -100:
            raise ValueError("A motor can only be between -100 and 100")
        self.valMotorB = valMotorB
        self.setMotors()
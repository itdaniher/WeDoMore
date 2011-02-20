import sys
import usb.core
import usb.util

from array import array

from WeDoDefs import *

WeDo = usb.core.find(idVendor=0x0694, idProduct=0x0003)

if WeDo is None:
	sys.exit("Can't find Lego WeDo")

if WeDo.is_kernel_driver_active(0):
	try:
		WeDo.detach_kernel_driver(0)
	except usb.core.USBError as e:
		sys.exit("Could not detatch kernel driver: %s" % str(e))

def WeDoGet():
	"""Use recursion to clean out the ±1 LSB offset issue."""
	endpoint = WeDo[0][(0,0)][0]
	data = list(endpoint.read(64)[-8:])
	if data[5] != 231:
		return data
	else:
		return WeDoGet()

def WeDoWrite(motorA, motorB):
	"""Arguments should be in form of a number between 0 and 127, positive or negative. Magic numbers used for the ctrl_transfer derived from sniffing USB coms."""
	motorA = int(motorA)
	motorB = int(motorB)
	magicNumber = 64
	data = [magicNumber, motorA&0xFF, motorB&0xFF, 0x00, 0x00, 0x00, 0x00, 0x00]
	WeDo.ctrl_transfer(bmRequestType = 0x21, bRequest = 0x09, wValue = 0x0200, wIndex = 0, data_or_wLength = data)

lshift = lambda x: x >> 1

def getData():
	rawData = map(lshift, WeDoGet())
	sensorData = {rawData[3]: rawData[2], rawData[5]: rawData[4]}
	return (rawData, sensorData)

distanceSensorIDS = [88, 89]



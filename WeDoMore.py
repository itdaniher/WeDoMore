#code released under a beerware license.
#Ian Daniher - Mar6 2011

import sys
import usb.core


class WeDo:
	def __init__(self):
		"""Find a USB device with the VID and PID of the Lego WeDo. If the HID kernel driver is active, detatch it."""
		self.dev = usb.core.find(idVendor=0x0694, idProduct=0x0003)
		if self.dev is None:
			sys.exit("Can't find Lego WeDo")
		if self.dev.is_kernel_driver_active(0):
			try:
				self.dev.detach_kernel_driver(0)
			except usb.core.USBError as e:
				sys.exit("Could not detatch kernel driver: %s" % str(e))

	def getRawData(self):
		"""Read 64 bytes from the WeDo's endpoint, but only return the last eight."""
		self.endpoint = self.dev[0][(0,0)][0]
		data = list(self.endpoint.read(64)[-8:])
		return data

	def writeMotor(self, valMotorA, valMotorB):
		"""Arguments should be in form of a number between 0 and 127, positive or negative. Magic numbers used for the ctrl_transfer derived from sniffing USB coms."""
		motorA = int(valMotorA)
		motorB = int(valMotorB)
		#create databuffer using motor values and magic motor-control number
		data = [64, valMotorA&0xFF, valMotorB&0xFF, 0x00, 0x00, 0x00, 0x00, 0x00]
		self.dev.ctrl_transfer(bmRequestType = 0x21, bRequest = 0x09, wValue = 0x0200, wIndex = 0, data_or_wLength = data)


	def getData(self):
		"""Sensor data is contained in the 2nd and 4th byte, with sensor IDs being contained in the 3rd and 5th byte respectively."""
		rawData = self.getRawData()
		sensorData = {rawData[3]: rawData[2], rawData[5]: rawData[4]}
		return sensorData

	def processTilt(self, v):
		"""Use a series of elif/value-checks to process the tilt sensor data."""
		if v == 27:
			return 3
		elif v == 74:
			return 2
		elif v == 180:
			return 0
		elif v == 230:
			return 1
		else:
			return 0

	def interpretData(self):
		"""This function contains all the magic-number sensor/actuator IDs. It returns a list containing one or two tuples of the form (name, value)."""
		data = self.getData()
		response = []
		for num in data.keys():
			if num in [0, 1, 2]:
				response.append( ('motor', 1) )
			elif num in [176, 177, 178, 179]: 
				response.append( ('distance', data[num]-39) )
			elif num in [38, 39]: 
				response.append( ('tilt', self.processTilt(data[num])) )
			elif num in [238, 239]:
				response.append( ('motor', 0) )
			elif num in [228, 230]: 
				response.append( ('normal', 1) )
		return response

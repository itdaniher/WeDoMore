import sys
import usb.core

WeDo = usb.core.find(idVendor=0x0694, idProduct=0x0003)

if WeDo is None:
	sys.exit("Can't find Lego WeDo")

if WeDo.is_kernel_driver_active(0):
	try:
		WeDo.detach_kernel_driver(0)
	except usb.core.USBError as e:
		sys.exit("Could not detatch kernel driver: %s" % str(e))

def WeDoGet():
	endpoint = WeDo[0][(0,0)][0]
	data = list(endpoint.read(64)[-8:])
	return data

def WeDoWrite(motorA, motorB):
	"""Arguments should be in form of a number between 0 and 127, positive or negative. 
Magic numbers used for the ctrl_transfer derived from sniffing USB coms."""
	motorA = int(motorA)
	motorB = int(motorB)
	magicNumber = 64
	data = [magicNumber, motorA&0xFF, motorB&0xFF, 0x00, 0x00, 0x00, 0x00, 0x00]
	WeDo.ctrl_transfer(bmRequestType = 0x21, bRequest = 0x09, wValue = 0x0200, wIndex = 0, data_or_wLength = data)


def getData():
	rawData = WeDoGet()
	sensorData = {rawData[3]: rawData[2], rawData[5]: rawData[4]}
	return sensorData

def processTilt(v):
	if v < 49:
		return 3
	elif v < 100:
		return 2
	elif v < 154:
		return 0
	elif v < 205:
		return 1
	else:
		return 0

def interpretData():
	data = getData()
	response = []
	for num in data.keys():
		if num in [0, 1, 2]:
			response.append( ('motor', 1) )
		elif num in [176, 177, 178, 179]: 
			response.append( ('distance', data[num]-39) )
		elif num in [38, 39]: 
			response.append( ('tilt', processTilt(data[num])) )
		elif num in [238, 239]:
			response.append( ('motor', 0) )
		elif num in [228, 230]: 
			response.append( ('normal', 1) )
	return response

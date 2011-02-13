import sys
import usb.core
import usb.util

from WeDoDefs import *

WeDo = usb.core.find(idVendor=0x0694, idProduct=0x0003)

if WeDo is None:
	sys.exit("Can't find Lego WeDo")

endpoint = device[0][(0,0)][0]

data += WeDo.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)




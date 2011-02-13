tiltID = 2
distanceID = 9
lightID = 10
motorID = 13
#motor takes a signed 8-bit number

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

#!/usr/bin/python
'''
Thibaut Colar
http://wiki.colar.net/

Quick (&dirty) script that takes in an usbmon log (USB sniffer)
and dumps out an easier to read html file.
This is used to debug/rev. engineer USB protocols under linux/unix.

What it adds to a usbmon log:
- colors so it's easier to scan through
- timestamps shown as time offsets - easier to see where we are at
- data packets shown in ascii as well as hex (ascii helps seing commands)
etc...

Example of use:
--- Doing an USBMon trace ---
	# mount -t debugfs none_debugs /sys/kernel/debug
	# sudo modprobe usbmon
If you want to scan a specific dveice, find it's device number (sudo lsusb)
	$ sudo cat /sys/kernel/debug/usbmon/4u > /tmp/usb.log
run some usb transactions of some kind :-)
when done kill the 'cat' command (^c)
--- Converting to HTML ----
	#python usbmon_helper /tmp/usb.log > /tmp/usb.html
Open /tmp/usb.html in browser and enjoy !

USBMon Doc:
http://www.mjmwired.net/kernel/Documentation/usb/usbmon.txt
'''

from optparse import OptionParser
import re
import string

time_style="font-weight:bold"
data_hex_style="color:#000000"
data_ascii_style="color:#000066"
type_styles={	'S': "color:#006600;font-weight:bold", #submission
				'C': "color:#000066;font-weight:bold", # callback
				'E': "color:#990000;font-weight:bold"# error
}

address_styles={'Bo': "color:#006600;font-weight:bold",
				'Bi': "color:#000066;font-weight:bold",
				'Co': "color:#009900;font-weight:bold",
				'Ci': "color:#000099;font-weight:bold",
				'Zo': "color:#00CC00;font-weight:bold",
				'Zi': "color:#0000CC;font-weight:bold",
				'Io': "color:#003300;font-weight:bold",
				'Ii': "color:#000033;font-weight:bold"
} 

ep_styles={	0: "color:#6d9c08;font-weight:bold",
			1: "color:#bb0e5b;font-weight:bold",
			2: "color:#bb670e;font-weight:bold",
			3: "color:#8a0ebb;font-weight:bold",
			4: "color:#0ebb81;font-weight:bold",
			5: "color:#bb130e;font-weight:bold",
			6: "color:#0eb5bb;font-weight:bold",
			7: "color:#9c8b08;font-weight:bold",
			8: "color:#bb0ea1;font-weight:bold",
			9: "color:#470ebb;font-weight:bold",

}

def parse_cmd():
	usage = usage = "usage: %prog usbmon_log_file [options] > output_file.html\n"
	parser = OptionParser(usage)
	parser.add_option("-b", "--basic", action="store_true", dest="basic", help="Dump less data, so it can be 'diffed' more easily")
	parser.add_option("-d", "--data", action="store_true", dest="data", help="Dump data packets only (no control/empty packets)")
	return parser.parse_args()

def hex_to_ascii(hex):
	text=''
	for i in range(len(hex)/2):
		nb=int(hex[i*2:i*2+2], 16)
		if(nb >= 32 and nb <= 126):
			text += chr(nb)
		else:
			text += "."
	return text

###### MAIN ###########
(options, args)=parse_cmd()
filein=args[0]
basic=options.basic
data_only=options.data
file = open(filein,"r")
lines = file.readlines()

pattern = re.compile('(\S+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*)')

timeref=0
if not basic:
	print "<html><body><h4>"
	print "<b>Time:</b> Time offset from first packet (MM:SS.mmmm)<br/>"
	print "<b>Type:</b> S: submission, C: control, E: Error<br/>"
	print "<b>Address:</b> Address (URB type and direction, Bus number, Device address, Endpoint nb)<br/>"
	print "&nbsp;&nbsp; - URB type and direction: <br/>"
	print "&nbsp;&nbsp;&nbsp;&nbsp;Ci Co   Control input and output<br/>"
	print "&nbsp;&nbsp;&nbsp;&nbsp;Zi Zo   Insochronous input and output<br/>"
	print "&nbsp;&nbsp;&nbsp;&nbsp;Ii Io   Interrupt input and output<br/>"
	print "&nbsp;&nbsp;&nbsp;&nbsp;Bi Bo   Bulk input and output<br/>"
	print "<b>Status:</b> Status Code returned<br/></h4>"
print "<table border=1 style='font-size:14px'>"
if not basic:
	print "<tr><th>URB Tag</th><th>Time</th><th>Type</th><th>Address</th><th>Status</th><th>Length</th><th>Data</th></tr>"
else:
	print "<tr><th>Status</th><th>Length</th><th>Data</th></tr>"

for line in lines:
	m = pattern.match(line)
	if m:
		data=None
		[urbtag,time,type,address,status,length,trail] = m.groups()
		if timeref == 0:
			timeref=string.atoi(time)
		time_offset=string.atoi(time)-timeref
		# FIXME
		nice_time=""+str(time_offset/60000000)+":"+str(time_offset%60000000/1000000)+"."+str(time_offset%1000000/1000)

		if not re.match("-?\d+", status):
			# no data length
			trail=length+" "+trail
			length=""

		if len(length) >0 and string.atoi(length) > 30:
			# usbmon only grabs first 30 bytes apparently.
			length="<font color='#ff0000'>"+length+"</font>"

		if len(trail)>0:
			sign=trail[0]
			if sign == '>':
				trail="<font color='006600'>&gt;</font>"+trail[1:]
			elif sign == '<':
				trail="<font color='000066'>&lt;</font>"+trail[1:]
			elif sign == '=':
				# data
				data=trail[1:]
				data_nospaces=data.replace(' ','')
				trail="= <font style='"+data_hex_style+"'>"+data+"</font><br/><font style='"+data_ascii_style+"'>["+hex_to_ascii(data_nospaces)+"]</font>"

		epindex=address.rfind(":")+1
		ep=address[epindex:]
		address="<font style='"+address_styles[address[0:2]]+"'>"+address[0:2]+"</font>"+address[2:epindex]+"<font style='"+ep_styles[string.atoi(ep)%10]+"'>"+ep+"</font>"

		if not (data_only and data == None):
			print "<tr>"
			if not basic:
				print "<td>"+urbtag+"</td>",
				print "<td style='"+time_style+"'>"+nice_time+"</td>",
				print "<td style='"+type_styles[type]+"'>"+type+"</td>",
				print "<td>"+address+"</td>",
			print "<td>"+status+"</td>",
			print "<td>"+length+"</td>",
			print "<td>"+trail+"</td>",
			print "</tr>"
	else:
		if not basic:
			print "<tr><td colspan=7>"+line+"</td></tr>"
		else:
			print "<tr><td colspan=3>"+line+"</td></tr>"

print "</table></body></html>"

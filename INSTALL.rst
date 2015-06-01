Add your user on in the usb group or add this file to this rule to udev.d :

SYSFS{idVendor}=="0694", SYSFS{idProduct}=="0003", MODE="0666"

For Ubuntu Linux 14.04 and newer, the udev syntax has changed.

In a file called /etc/udev/rules.d/lego-wedo.rules: Add the following line:

    SUBSYSTEM=="usb", ATTR{idVendor}=="0694", ATTR{idProduct}=="0003", MODE:="0666"

Note the colon on the MODE assignment and the use of ATTR.

Add your user on in the usb group or add this file to this rule to udev.d :

SYSFS{idVendor}=="0694", SYSFS{idProduct}=="0003", MODE="0666"

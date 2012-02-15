#!/bin/bash

#packaging script to build a TurtleArt plugin.

cp -r PyUSB/usb wedo_plugin 
echo "copied importable copy of PyUSB to the plugin directory"
cp WeDoMore.py wedo_plugin
echo "copied importable copy of WeDoMore to the plugin directory"
cp README.mkd wedo_plugin/README
echo "copied README file to the plugin directory"

#!/bin/bash

# Command to run the website
WEB_COMMAND="/usr/bin/python2 /home/pi/3rdYearProject/Website/main.py"
BLOB_COMMAND="/usr/bin/python2 /home/pi/3rdYearProject/ImageAnalysis/detect.py"

# Kill website if it's already running
sudo kill $(ps aux | grep -E "^root.*${WEB_COMMAND}$" | cut -d ' ' -f7,8) 2>/dev/null

# Kill blob detection if it's already running
sudo kill $(ps aux | grep -E "${BLOB_COMMAND}$" | grep -v grep | cut -d ' ' -f9) 2>/dev/null

#!/bin/bash

# Close previous instances, if they exist
. /home/pi/3rdYearProject/stopSystem.sh

# Run website and blob detection
$WEB_COMMAND & $BLOB_COMMAND &

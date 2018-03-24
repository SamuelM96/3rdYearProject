#!/bin/bash
COUNT=2

gphoto2 --set-config /main/capturesettings/imagequality=0 \
        --set-config-index /main/capturesettings/rawcompression=1 \
        --set-config-index /main/capturesettings/capturemode=1 \
        --set-config-index /main/settings/capturetarget=1 \
        --set-config-value /main/capturesettings/burstnumber=$COUNT \
        --frames 10 --interval 1 \
        --capture-image-and-download

# gphoto2 --set-config /main/capturesettings/imagequality=0 \
#         --set-config-index /main/capturesettings/rawcompression=1 \
#         --frames 5 --interval 1 \
#         --capture-image-and-download
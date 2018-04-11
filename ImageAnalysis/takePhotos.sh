#!/bin/bash
COUNT=4

gphoto2 --set-config /main/capturesettings/imagequality=0 \
        --set-config-index /main/settings/capturetarget=1 \
        --set-config-index /main/capturesettings/capturemode=1 \
        --set-config /main/actions/autofocusdrive=1 \
        --set-config /main/capturesettings/burstnumber=$COUNT \
        --frames 1 \
        --trigger-capture
        # --capture-image-and-download
        # --set-config-index /main/settings/capturemode=0 \

# gphoto2 --set-config /main/capturesettings/imagequality=0 \
#         --set-config-index /main/capturesettings/rawcompression=1 \
#         --set-config-index /main/capturesettings/capturemode=1 \
#         --set-config-index /main/settings/capturetarget=1 \
#         --set-config-value /main/capturesettings/burstnumber=$COUNT \
#         --frames 10 --interval 1 \
#         --capture-image-and-download

# gphoto2 --set-config /main/capturesettings/imagequality=0 \
#         --set-config-index /main/capturesettings/rawcompression=1 \
#         --frames 5 --interval 1 \
#         --capture-image-and-download

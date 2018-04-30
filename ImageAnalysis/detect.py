#!/usr/bin/python2

import threading
import zmq
import select
import numpy as np
import math
import cv2
from picamera import PiCamera
import pyximport; pyximport.install()
import findBlobs as fb

# Automated tracking toggle
AUTO_MODE = False

# Setup details
WIDTH = 640
HEIGHT = 480
HWIDTH = WIDTH/2
HHEIGHT = HEIGHT/2
DSLR_CENTER_Y = HHEIGHT - 20

# Retreives just the luminescence data from a camera setup with the YUV420 image format
class Luminescence():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = None

    def write(self, buf):
        self.data = np.frombuffer(buf, dtype=np.uint8, count=self.width*self.height).reshape((self.height,self.width))


# Receives messages from the server
def getData(socket):
    global AUTO_MODE
    global DSLR_CENTER_Y
    while True:
        message = socket.recv()
        print "Received message: " + message

        # Toggle automated tracking on/off
        if message == "MANUAL_TOGGLE":
            AUTO_MODE = not AUTO_MODE
            if AUTO_MODE:
                print "Mode: AUTO"
            else:
                print "Mode: Manual"
        elif message.startswith("HEIGHT_COMP: "):
            val = message.split(' ')[1]
            try:
                DSLR_CENTER_Y = HHEIGHT + int(val)
            except ValueError:
                pass

def main():
    # Setup interprocess communication with blob detector
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://localhost:5555")

    # Background thread to receive server messages
    backgroundThread = threading.Thread(target=getData, args = (socket,))
    backgroundThread.daemon = True
    backgroundThread.start()

    # Contains found blobs
    blobs = []

    # Number of steps from the edge to reach the center
    PAN_STEPS_TO_CENTER = 66
    PAN_STEP_CONV = float(PAN_STEPS_TO_CENTER)/HWIDTH
    TILT_STEPS_TO_CENTER = 220
    TILT_STEP_CONV = float(TILT_STEPS_TO_CENTER)/HHEIGHT

    # Camera setup
    camera = PiCamera()
    camera.resolution = (WIDTH, HEIGHT)
    camera.framerate = 49
    camera.sensor_mode = 5
    camera.exposure_mode = 'sports'

    # Gets luminescence data
    lumi = Luminescence(WIDTH, HEIGHT)

    # Tracking params
    lumiLevel = 5
    trackedBlob = None
    maxBlobSize = 80
    minBlobSize = 10
    decelerationAmount = 0.75

    # Process camera frames
    for cap in camera.capture_continuous(lumi, format="yuv", use_video_port=True):
        frame = cap.data[:HEIGHT-20,:]
        frame.flags.writeable = True

        # Find blobs in the image
        blobs = fb.findBlobs(frame, blobs, lumiLevel, maxBlobSize, minBlobSize)

        # Process blobs
        closestBlobToCenter = None
        cBlobCenter = ()
        cBlobDistSq = None
        blobCenter = ()
        blobDistSq = -1
        found = False
        for b in blobs:
            if b.alive == 1:
                blobCenter = (b.rect[0] + (b.rect[2] - b.rect[0]) / 2, b.rect[1] + (b.rect[3] - b.rect[1]) / 2)
                blobDistSq = (blobCenter[0] - HWIDTH)**2 + (blobCenter[1] - DSLR_CENTER_Y)**2

                # Draw bounding boxes and IDs
                cv2.rectangle(frame, (b.rect[0], b.rect[1]), (b.rect[2], b.rect[3]), (128, 0, 0), 3)
                cv2.putText(frame, str(b.num), blobCenter, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 0), 2)

                if trackedBlob is not None and b.num == trackedBlob.num:
                    # Found blob that needs to be tracked
                    found = True
                    trackedBlob = b
                    break
                elif closestBlobToCenter is None or blobDistSq < cBlobDistSq:
                    # Find closest blob to the center of the DSLRs view, in case tracked blob is lost
                    closestBlobToCenter = b
                    cBlobCenter = blobCenter
                    cBlobDistSq = blobDistSq

            # Lost tracked blob, so track blob closest to DSLRs center
            if found == False:
                if closestBlobToCenter is not None:
                    trackedBlob = closestBlobToCenter
                    blobCenter = cBlobCenter
                    blobDistSq = cBlobDistSq
                else:
                    # No blobs found, reset tracked blob
                    trackedBlob = None


        # Automated tracking mode
        if AUTO_MODE:
            # Move system to blobs new position
            if trackedBlob is not None:
                panSteps = int(PAN_STEP_CONV * (blobCenter[0] - HWIDTH) * decelerationAmount)
                tiltSteps = int((TILT_STEP_CONV * (DSLR_CENTER_Y - blobCenter[1])) * decelerationAmount)
                
                # Dead zone check
                panPadding = 4
                tiltPadding = 10
                if panSteps < panPadding and panSteps > -panPadding:
                    panSteps = 0
                if tiltSteps < tiltPadding and tiltSteps > -tiltPadding:
                    tiltSteps = 0

                # Tell server where to move
                message = str(panSteps) + "," + str(tiltSteps)
                socket.send_string(message)

        # Draw center of DSLR dot for visual help
        cv2.rectangle(frame, (HWIDTH, DSLR_CENTER_Y), (HWIDTH, DSLR_CENTER_Y), (128, 0, 0), 3)

        # Show camera display
        cv2.imshow('image', frame)

        # Loop until 'q' is pressed to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cv2.destroyAllWindows()

main()

from multiprocessing.dummy import Pool as ThreadPool
import numpy as np
import cv2
# from picamera.array import PiRGBArray
# from picamera import PiCamera
import pyximport; pyximport.install()
import findBlobs as fb


def main():
    blobs = []
    WIDTH = 640
    HEIGHT = 480
    HWIDTH = WIDTH/2
    HHEIGHT = HEIGHT/2
    STEP_CONV = 1
    cap = cv2.VideoCapture(0) 
    # camera = PiCamera()
    # camera.resolution = (WIDTH, HEIGHT)
    # camera.framerate = 32
    # rawCapture = PiRGBArray(camera, size=(WIDTH, HEIGHT))
    trackedBlob = None

    # Process camera frames
    while True:
        ret, frame = cap.read()
    # for frameCam in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # frame = frameCam.array
        # frame.flags.writeable = True
        
        # Find blobs in the image
        blobs = fb.findBlobs(frame, blobs)
        
        # Process blobs
        closestBlobToCenter = None
        cBlobCenter = ()
        cBlobDistSq = None
        blobCenter = ()
        blobDistSq = -1
        found = False
        for b in blobs:
            blobCenter = (b.rect[0] + (b.rect[2] - b.rect[0]) / 2, b.rect[1] + (b.rect[3] - b.rect[1]) / 2)
            blobDistSq = (blobCenter[0] - HWIDTH)**2 + (blobCenter[1] - HHEIGHT)**2

            if trackedBlob is not None and b.num == trackedBlob.num:
                # Found blob that needs to be tracked
                found = True
                trackedBlob = b
                break
            elif closestBlobToCenter is None or distSq < cBlobDist:
                # Find closest blob to the center, in case tracked blob is lost
                closestBlobToCenter = b
                cBlobCenter = blobCenter
                cBlobDistSq = distSq

            # Draw bounding boxes and IDs
            if b.alive == 1:
                cv2.rectangle(frame, (b.rect[0], b.rect[1]), (b.rect[2], b.rect[3]), (128, 0, 0), 3)
                cv2.putText(frame, str(b.num), blobCenter, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 0), 2)

        # Lost tracked blob, so track blob closest to center
        if found == False:
            if closestBlobToCenter is not None:
                trackedBlob = closestBlobToCenter
                blobCenter = cBlobCenter
                blobDistSq = cBlobDistSq
            else:
                # No blobs found, reset tracked blob
                trackedBlob = None

        # Move system to blobs new position
        if trackedBlob is not None:
            steps = sqrt(distSq) * STEP_CONV

        # Show camera display
        cv2.imshow('image', frame)
        # rawCapture.truncate(0)

        # Loop until 'q' is pressed to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()

main()

from multiprocessing.dummy import Pool as ThreadPool
import numpy as np
import cv2
# from picamera.array import PiRGBArray
# from picamera import PiCamera
import pyximport; pyximport.install()
import findBlobs as fb


def main():
    cap = cv2.VideoCapture(0) 
    blobs = []
    # camera = PiCamera()
    # camera.resolution = (640, 480)
    # camera.framerate = 32
    # rawCapture = PiRGBArray(camera, size=(640, 480))

    while True:
        ret, frame = cap.read()
    # for frameCam in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # frame = frameCam.array
        # frame.flags.writeable = True
        
        # Find blobs in the image
        blobs = fb.findBlobs(frame, blobs)
        
        # Process blobs
        for i in xrange(len(blobs)-1,-1,-1):
            b = blobs[i]
            
            # Draw bounding boxes and IDs of blobs
            elif b.alive == 1: 
                cv2.rectangle(frame, (b.rect[0], b.rect[1]),
                          (b.rect[2], b.rect[3]), (128, 0, 0), 3)
                cv2.putText(frame, str(b.num), (b.rect[0] + (b.rect[2] - b.rect[0]) / 2, b.rect[1] + (b.rect[3] - b.rect[1]) / 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 0), 2)

        cv2.imshow('image', frame)
        # rawCapture.truncate(0)

        # Loop until 'q' is pressed to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()


main()

from multiprocessing.dummy import Pool as ThreadPool
import numpy as np
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import pyximport; pyximport.install()
import findBlobs as fb


def main():
    # cap = cv2.VideoCapture("G:/Google Drive/University/Year 3/Project/3rdYearProject/ImageAnalysis/test.avi")
    # cap = cv2.VideoCapture(0) 
    blobs = []
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))

    # while True:
    for frameCam in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # ret, frame = cap.read()
        frame = frameCam.array
        frame.flags.writeable = True
        blobs = fb.findBlobs(frame, blobs)
        

        for b in blobs:
            cv2.rectangle(frame, (b.rect[0], b.rect[1]),
                          (b.rect[2], b.rect[3]), (128, 0, 0), 3)
            cv2.putText(frame, str(b.num), tuple(b.center),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 0), 2)

        cv2.imshow('image', frame)
        rawCapture.truncate(0)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # cap.release()
    cv2.destroyAllWindows()


main()

from multiprocessing.dummy import Pool as ThreadPool
import numpy as np
import cv2
import pyximport; pyximport.install()
import findBlobs as fb


def main():
    # cap = cv2.VideoCapture("G:/Google Drive/University/Year 3/Project/3rdYearProject/ImageAnalysis/test.avi")
    cap = cv2.VideoCapture(0) 
    blobs = []

    while cap.isOpened():
        ret, frame = cap.read()
        # frame = cv2.blur(frame, (30,30))
        # frame = cv2.imread("G:/Google Drive/University/Year 3/Project/3rdYearProject/ImageAnalysis/DSC_0681.png")
        # frame = cv2.resize(frame, (0, 0), fx=0.3, fy=0.3)
        blobs = fb.findBlobs(frame, blobs)
        

        for b in blobs:
            cv2.rectangle(frame, (b.rect[0], b.rect[1]),
                          (b.rect[2], b.rect[3]), (128, 0, 0), 3)
            cv2.putText(frame, str(b.num), tuple(b.center),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 128, 0), 2)

        cv2.imshow('image', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


main()

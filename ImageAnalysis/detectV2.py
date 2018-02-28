from multiprocessing.dummy import Pool as ThreadPool
import numpy as np
import cv2
import pyximport; pyximport.install()
import findBlobs as fb


def main():
    cap = cv2.VideoCapture(0)
    blobs = []

    while True:
        ret, frame = cap.read()
        blobs = fb.findBlobs(frame, blobs)

        for b in blobs:
            cv2.rectangle(frame, (b.rect[0], b.rect[1]),
                          (b.rect[2], b.rect[3]), (128, 0, 0), 3)
            cv2.putText(frame, str(b.num), tuple(b.center),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 128, 0))

        cv2.imshow('image', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


main()

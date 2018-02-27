from multiprocessing.dummy import Pool as ThreadPool
import numpy as np
import cv2
import pyximport; pyximport.install()
import findBlobs as fb


def main():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        chunkBlobs = fb.findBlobs(frame)

        for b in chunkBlobs:
            cv2.rectangle(frame, (b.rect[0], b.rect[1]),
                          (b.rect[2], b.rect[3]), (0, 0, 0), 3)

        cv2.imshow('image', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


main()

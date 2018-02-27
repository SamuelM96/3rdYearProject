import numpy as np
import cv2


class Blob:
    def __init__(self, x, y):
        self.rect = [x, y, x, y]
        self.center = (x, y)

    def addPoint(self, x, y):
        changed = False
        if x < self.rect[0]:
            self.rect[0] = x
            changed = True
        elif x > self.rect[2]:
            self.rect[2] = x
            changed = True
        if y < self.rect[1]:
            self.rect[1] = y
            changed = True
        elif y > self.rect[3]:
            self.rect[3] = y
            changed = True
        if changed:
            self.center = (self.rect[0] + (self.rect[2] - self.rect[0]) / 2,
                           self.rect[1] + (self.rect[3] - self.rect[1]) / 2)

    def inRange(self, x, y):
        distSq = ((x - self.center[0])**2 + (y - self.center[1])**2)
        return distSq < 10000

def findBlobs(unsigned char [:, :, :] image):
    blobs = []
    lastBlob = None
    cdef int x, y, w, h
    cdef unsigned char val

    h = image.shape[0]
    w = image.shape[1]

    for y in xrange(0, h):
        for x in xrange(0, w):
            val = image[y,x,1]
            if val < 30:
                newBlob = True
                if lastBlob is not None and lastBlob.inRange(x, y):
                    lastBlob.addPoint(x, y)
                else:
                    for b in blobs:
                        if b.inRange(x, y):
                            b.addPoint(x, y)
                            lastBlob = b
                            newBlob = False
                            break
                    if newBlob:
                        lastBlob = Blob(x, y)
                        blobs.append(lastBlob)

    return blobs

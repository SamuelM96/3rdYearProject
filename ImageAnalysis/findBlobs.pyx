from cpython cimport array
import array
import numpy as np
import cv2
from sys import maxint


cdef class Blob:
    cdef public int num
    cdef public int [:] rect, center, lineStart, lastPixel 
    # cdef public int [:] center

    def __init__(self, int num, int x, int y):
        self.num = num
        self.rect = array.array('i', [x, y, x, y])
        self.center = array.array('i', [x, y])
        self.lineStart = array.array('i', [x, y])
        self.lastPixel = array.array('i', [x, y])

    cpdef addPoint(self, int x, int y):
        cdef int changed = 0
        if x < self.rect[0]:
            self.rect[0] = x
            changed = 1
        elif x > self.rect[2]:
            self.rect[2] = x
            changed = 1
        if y < self.rect[1]:
            self.rect[1] = y
            changed = 1
        elif y > self.rect[3]:
            self.rect[3] = y
            changed = 1
        if changed == 1:
            self.center[0] = self.rect[0] + (self.rect[2] - self.rect[0]) / 2
            self.center[1] = self.rect[1] + (self.rect[3] - self.rect[1]) / 2

    cpdef inRange(self, int x, int y):
        # cdef float l2 = self.rect[2] - self.rect[0]
        # if (l2 == 0):
        #     return ((x - self.rect[0])**2 + (y - self.rect[1])**2) < 100000
        # cdef float [:] vec = array.array('f', [l2, self.rect[3] - self.rect[1]])
        # cdef float t = max(0, min(1, np.dot([x - self.rect[0], y - self.rect[3]], vec) / l2))
        # vec[0] = self.rect[0] + t * vec[0]
        # vec[1] = self.rect[1] + t * vec[1]
        return ((x - self.center[0])**2 + (y - self.center[1])**2) < 100000
        # if y > self.lineStart[1]:
        #     distSq = ((x - self.lineStart[0])**2 + (y - self.lineStart[1])**2)
        #     if distSq < 50:
        #         self.lineStart[0] = x
        #         self.lineStart[1] = y
        #         self.lastPixel[0] = x
        #         self.lastPixel[1] = y
        #         return True
        # elif x - self.lastPixel[0] < 10:
        #     self.lastPixel[0] = x
        #     self.lastPixel[1] = y
        #     return True
        # else:
        #     return False

cpdef findBlobs(unsigned char [:, :, :] image, list blobs):
    cdef int counter = 0
    cdef list currentBlobs = []
    cdef Blob lastBlob = None
    cdef int x, y, w, h
    cdef unsigned char val

    h = image.shape[0]
    w = image.shape[1]

    for y in xrange(0, h):
        for x in xrange(0, w):
            val = image[y,x,1]
            if val < 10:
                newBlob = True
                if lastBlob is not None and lastBlob.inRange(x, y):
                    lastBlob.addPoint(x, y)
                else:
                    for b in currentBlobs:
                        if b.inRange(x, y):
                            b.addPoint(x, y)
                            lastBlob = b
                            newBlob = False
                            break
                    if newBlob:
                        counter += 1
                        lastBlob = Blob(counter, x, y)
                        currentBlobs.append(lastBlob)

    lenCBlobs = len(currentBlobs)

    if len(blobs) == 0:
        return currentBlobs
    elif len(blobs) == lenCBlobs:
        for i in xrange(lenCBlobs):
            b1 = currentBlobs[i]
            dist = maxint
            blobNum = 0
            for j in xrange(len(blobs)):
                b2 = blobs[j]
                newDist = ((b2.center[0] - b1.center[0])** 2 + (b2.center[1] - b2.center[1])**2)
                if newDist < 1000 and newDist < dist:
                    dist = newDist
                    blobNum = j
            b1.num = blobs[blobNum].num
            del blobs[blobNum]
            

    return currentBlobs

from cpython cimport array
import array
import numpy as np
import cv2
from sys import maxint
from random import randint
from math import ceil


cdef class Blob:
    cdef public int num, lastPixelX, alive, iteration, pixelCount
    cdef public int [:] rect, center, lineStart
    # cdef public unsigned char [:] lastLine

    def __init__(self, int num, int x, int y):
        self.num = num
        self.rect = array.array('i', [x, y, x, y])
        self.center = array.array('i', [x, y])
        self.lineStart = array.array('i', [x, y])
        self.lastPixelX = x
        self.alive = 1
        self.iteration = 5
        # self.lastLine = np.zeros(int(ceil(width/8.0)), dtype='B')
        self.pixelCount = 0

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
        
        self.pixelCount += 1

    # print "D: %d, x: %d, y: %d, lx: %d, ly: %d, lpx: %d" % (dist, x, y, self.lineStart[0], self.lineStart[1], self.lastPixelX)
    cpdef inRange(self, int x, int y):
        # return ((x - self.center[0])**2 + (y - self.center[1])**2) < 100000
        # result = False
        # if y != self.lineStart[1]:
        #     if ((x - self.lineStart[0]) **2 + (y - self.lineStart[1])**2) < 1000:
        #         self.lineStart[0] = x
        #         self.lineStart[1] = y
        #         self.lastPixelX = x
        #         return True
        # elif x - self.lastPixelX < 100: 
        #     self.lastPixelX = x
        #     return True

        # return False
        return y < self.rect[3] + 50 and x > self.rect[0] - 50 and x < self.rect[2] + 50

cpdef findBlobs(unsigned char [:, :, :] image, list blobs):
    cdef list currentBlobs = []
    cdef Blob lastBlob = None
    cdef int x, y, w, h
    cdef unsigned char val

    h = image.shape[0]
    w = image.shape[1]

    for y in xrange(0, h):
        for x in xrange(0, w):
            b = image[y,x,0]
            g = image[y,x,1]
            r = image[y,x,2]
            # if (r+g)/2 < 50 and b > 100:
            # if g < 30:
            if (b+g+r)/3 < 50:
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
                        lastBlob = Blob(randint(0,1000), x, y)
                        currentBlobs.append(lastBlob)

    if len(blobs) == 0:
        return currentBlobs
    elif len(blobs) >= len(currentBlobs):
        for i in xrange(len(currentBlobs)-1,-1,-1):
            curBlob = currentBlobs[i]
            if curBlob.pixelCount < 1000:
                del blobs[i]
                continue

            dist = maxint
            b = -1
            for j in xrange(len(blobs)):
                blob = blobs[j]
                newDist = ((blob.center[0] - curBlob.center[0])** 2 + (blob.center[1] - blob.center[1])**2)
                if newDist < dist:
                    dist = newDist
                    b = j
            if b != -1:
                curBlob.num = blobs[b].num
                del blobs[b]
    else: # len(blobs) < len(currentBlobs)
        for i in xrange(len(blobs)-1, -1, -1):
            blob = blobs[i]
            dist = maxint
            b = None
            for j in xrange(len(currentBlobs)-1,-1,-1):
                curBlob = currentBlobs[j]

                if curBlob.pixelCount < 1000:
                    del currentBlobs[j]
                    continue
                    
                newDist = ((curBlob.center[0] - blob.center[0])**2 + (curBlob.center[1] - curBlob.center[1])**2)
                if newDist < dist:
                    dist = newDist
                    b = curBlob
            if b is not None:
                b.num = blob.num
                del blobs[i]


    for b in blobs:
        if b.iteration > 1:
            b.alive = 0
            b.iteration -= 1
            currentBlobs.append(b)

    return currentBlobs

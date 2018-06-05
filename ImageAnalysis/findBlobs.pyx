from cpython cimport array
import array
import numpy as np
import cv2
from sys import maxint
from random import randint
from math import ceil

cdef int AREA_CHECK = 30

# Stores information about the blobs in an image
cdef class Blob:
    cdef public int num         # Blob ID
    cdef public int alive       # If the blob is active (0 means it wasn't redetected)
    cdef public int iteration   # How many frames the blob can persist for when undetected
    cdef public int pixelCount  # Number of pixels within the blob
    cdef public int[:] rect     # Bounding rectangle: [TopLeftX, TopLeftY, BtmRightX, BtmRightY]

    # Creates a new Blob object
    # num : Blob ID
    # x : Initial pixel x coordinate
    # y : Initial pixel y coordinate
    def __init__(self, int num, int x, int y):
        self.num = num
        self.rect = array.array('i', [x, y, x, y])
        self.alive = 1
        self.iteration = 5

    # Adds a point to the blob
    # x : x coordinate of pixel
    # y : y coordinate of pixel
    cpdef addPixel(self, int x, int y):
        if x < self.rect[0]:
            self.rect[0] = x
        elif x > self.rect[2]:
            self.rect[2] = x
        elif y > self.rect[3]:
            self.rect[3] = y

    # Returns True if the give pixel coords are within range of the blob, False otherwise
    cpdef inRange(self, int x, int y):
        return y < self.rect[3] + AREA_CHECK and x > self.rect[0] - AREA_CHECK and x < self.rect[2] + AREA_CHECK

# Returns a list of founds blobs in the given image
# image : Image to search for blobs in
# blobs : Previously detected blobs if persistant detection is needed
# lumiLevel : Max pixel luminescence
# maxBlobSize : Maximum size of blob bounding box side
# minBlobSize : Minimum size of blob bounding box side
cpdef findBlobs(unsigned char[:, :] image, list blobs=[], int lumiLevel=20, int maxBlobSize=80, int minBlobSize=10):
    cdef list currentBlobs = [] # List of detected blobs
    cdef Blob lastBlob = None   # Last detected blob
    cdef int x, y, w, h         # x,y coords and width,height of image
    cdef unsigned char val      # Pixel value
    cdef int blobWidth, blobHeight # Blob bounding box dimensions

    # Height and width of image
    h = image.shape[0]
    w = image.shape[1]

    for y in xrange(0, h):
        for x in xrange(0, w):
            lumi = image[y, x]

            if lumi < lumiLevel:
                newBlob = True

                # Try to add the detected pixel to the last used blob as an optimisation
                if lastBlob is not None and lastBlob.inRange(x, y):
                    lastBlob.addPixel(x, y)
                else:
                    # Try to add pixel to an existing blob
                    for b in currentBlobs:
                        if b.inRange(x, y):
                            b.addPixel(x, y)
                            lastBlob = b
                            newBlob = False
                            break
                    # Pixel not in range of current blobs, so create a new blob
                    if newBlob:
                        lastBlob = Blob(randint(0, 1000), x, y)
                        currentBlobs.append(lastBlob)


    # Removes too large and small blobs
    for i in xrange(len(currentBlobs)-1, -1, -1):
        curBlob = currentBlobs[i]
        blobWidth = curBlob.rect[2] - curBlob.rect[0]
        blobHeight = curBlob.rect[3] - curBlob.rect[1]

        if (blobWidth > maxBlobSize or
            blobHeight > maxBlobSize or
                blobWidth < minBlobSize or
                blobHeight < minBlobSize):

                del currentBlobs[i]
                continue

    # Blob persistence:
    # Tries to find matching blobs (current blobs that are closest to previous blobs) and
    # assigns the previous blobs number to the current one
    if len(blobs) == 0:
        return currentBlobs
    elif len(blobs) >= len(currentBlobs):
        for i in xrange(len(currentBlobs)-1, -1, -1):
            curBlob = currentBlobs[i]
            blobWidth = curBlob.rect[2] - curBlob.rect[0]
            blobHeight = curBlob.rect[3] - curBlob.rect[1]

            # Finds closest previous blob based on distance between their centers
            dist = maxint
            b = -1
            for j in xrange(len(blobs)):
                blob = blobs[j]

                # Calculate distance between centers from bounding rectangles
                newDist = ((blob.rect[0] - curBlob.rect[0] +
                    (blob.rect[2] - blob.rect[0] - blobWidth) / 2)**2 +
                    (blob.rect[1] - curBlob.rect[1] +
                    (blob.rect[3] - blob.rect[1] - blobHeight) / 2)**2)

                if newDist < dist:
                    dist = newDist
                    b = j

            # Persist previous blobs number
            if b != -1:
                curBlob.num = blobs[b].num
                del blobs[b]
    else:  # len(blobs) < len(currentBlobs)
        for i in xrange(len(blobs)-1, -1, -1):
            blob = blobs[i]

            # Finds closest previous blob based on distance between their centers
            dist = maxint
            b = None
            for j in xrange(len(currentBlobs)-1, -1, -1):
                curBlob = currentBlobs[j]
                blobWidth = curBlob.rect[2] - curBlob.rect[0]
                blobHeight = curBlob.rect[3] - curBlob.rect[1]

                # Calculate distance between centers from bounding rectangles
                newDist = ((blob.rect[0] - curBlob.rect[0] +
                    (blob.rect[2] - blob.rect[0] - blobWidth) / 2)**2 +
                    (blob.rect[1] - curBlob.rect[1] +
                    (blob.rect[3] - blob.rect[1] - blobHeight) / 2)**2)

                if newDist < dist:
                    dist = newDist
                    b = curBlob

            # Persist previous blobs number
            if b is not None:
                b.num = blob.num
                del blobs[i]

    # Left over blobs are previous blobs that have "disappeared" (obscured, missed detection,
    # moved off screen, etc) which are allowed to survive for a set amount of frame so they can
    # be redetected and persist through newer blobs
    for b in blobs:
        if b.iteration > 1:
            b.alive = 0
            b.iteration -= 1
            currentBlobs.append(b)

    return currentBlobs

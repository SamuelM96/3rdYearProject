from cpython cimport array
import array
import numpy as np
import cv2
from sys import maxint
from random import randint
from math import ceil


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
        self.pixelCount = 0

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
        self.pixelCount += 1

    # Returns True if the give pixel coords are within range of the blob, False otherwise
    cpdef inRange(self, int x, int y):
        return y < self.rect[3] + 50 and x > self.rect[0] - 50 and x < self.rect[2] + 50

# Returns a list of founds blobs in the given image
# image : Image to search for blobs in
# blobs : Previously detected blobs if persistant detection is needed
cpdef findBlobs(unsigned char[:, :, :] image, list blobs=[]):
    cdef list currentBlobs = [] # List of detected blobs
    cdef Blob lastBlob = None   # Last detected blob
    cdef int x, y, w, h         # x,y coords and width,height of image
    cdef unsigned char val      # Pixel value

    # Height and width of image
    h = image.shape[0]
    w = image.shape[1]

    for y in xrange(0, h):
        for x in xrange(0, w):
            blue = image[y, x, 0]
            green = image[y, x, 1]
            red = image[y, x, 2]

            # Test brightness of pixel (threshold function)
            if (blue + green + red)/3 < 50:
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

    # Blob persistence:
    # Tries to find matching blobs (current blobs that are closest to previous blobs) and
    # assigns the previous blobs number to the current one
    if len(blobs) == 0:
        return currentBlobs
    elif len(blobs) >= len(currentBlobs):
        for i in xrange(len(currentBlobs)-1, -1, -1):
            curBlob = currentBlobs[i]

            # Removes small blobs
            if curBlob.pixelCount < 1000:
                del blobs[i]
                continue

            # Finds closest previous blob based on distance between their centers
            dist = maxint
            b = -1
            for j in xrange(len(blobs)):
                blob = blobs[j]
                
                # Calculate distance between centers from bounding rectangles
                newDist = (blob.rect[0] - curBlob.rect[0] + (blob.rect[2] - blob.rect[0] - curBlob.rect[2] + curBlob.rect[0]) / 2)**2 + (
                    blob.rect[1] - curBlob.rect[1] + (blob.rect[3] - blob.rect[1] - curBlob.rect[3] + curBlob.rect[1]) / 2)**2
                
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

                # Remove small blobs
                if curBlob.pixelCount < 1000:
                    del currentBlobs[j]
                    continue

                # Calculate distance between centers from bounding rectangles
                newDist = (blob.rect[0] - curBlob.rect[0] + (blob.rect[2] - blob.rect[0] - curBlob.rect[2] + curBlob.rect[0]) / 2)**2 + (
                    blob.rect[1] - curBlob.rect[1] + (blob.rect[3] - blob.rect[1] - curBlob.rect[3] + curBlob.rect[1]) / 2)**2
                
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

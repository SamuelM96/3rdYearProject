from multiprocessing.dummy import Pool as ThreadPool
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2


DISTSQ = 10000


class Blob:
    def __init__(self, x, y):
        self.rect = [x, y, x, y]
        self.points = [(x, y)]
        self.center = (x, y)

    def addPoint(self, x, y):
        self.points.append((x, y))

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
        # halfWidth = (self.rect[2] - self.rect[1])/2
        # halfHeight = (self.rect[1] - self.rect[3])/2
        # x,y = self.center
        
        # dx = max(abs(px - x) - halfWidth, 0)
        # dy = max(abs(py - y) - halfHeight, 0)
        # return (dx * dx + dy * dy) < DISTSQ
        distSq = ((x - self.center[0])**2 + (y - self.center[1])**2)
        # print distSq
        return distSq < DISTSQ


class Chunk:
    def __init__(self, padding, c):
        self.padding = padding
        self.c = c


def findBlobs1(chunk):
    blobs = []
    lastBlob = None
    for y, row in enumerate(chunk.c):
        for x, val in enumerate(row):
            if val == 0:
                y += chunk.padding
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


def findBlobs(chunk):
    blobs = []
    lastBlob = None
    for coords in chunk:
        y,x = coords
        if lastBlob is not None and lastBlob.inRange(x, y):
            lastBlob.addPoint(x, y)
        else:
            newBlob = True
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


def main():
    # cap = cv2.VideoCapture(0)
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))

    # while True:
    for frameCam in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # ret, frame = cap.read()
        frame = frameCam.array
        # frame = cv2.imread("G:/Google Drive/University/Year 3/Project/3rdYearProject/ImageAnalysis/DSC_0681.png", cv2.IMREAD_GRAYSCALE)
        # frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, gray = cv2.threshold(frame, 10, 255, cv2.THRESH_BINARY)
    # gray = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
    # col = Image.open("G:/Google Drive/University/Year 3/Project/3rdYearProject/ImageAnalysis/DSC_0681.png")
    # col = col.resize((col.width / 10, col.height / 10))
    # gray = col.convert('L')

    # Let numpy do the heavy lifting for converting pixels to pure black or white
    # bw = np.asarray(gray).copy()

    # Threshold image to become black/white to make blobs distinct
    # threshold = 50
    # bw[bw < threshold] = 0    # Black
    # bw[bw >= threshold] = 255  # White

    # Find blobs
        blobPixels = np.argwhere(gray == 0)
        # # numThreads = 1
        # pool = ThreadPool()
        # numElems = len(blobPixels) / 1
        # chunks = [blobPixels[i:i + numElems] for i in xrange(0, len(blobPixels), numElems)]
        # chunkBlobs = pool.map(findBlobs, chunks)
        chunkBlobs = findBlobs(blobPixels)
        # print chunkBlobs

    # Now we put it back in Pillow/PIL land
    # im = Image.fromarray(bw)
    # draw = ImageDraw.Draw(im)

    # for i in xrange(0, len(bw), numElems):
    #     draw.rectangle([0, i, len(bw[0]), i + numElems], outline=50)

        # for cb in chunkBlobs:
        for b in chunkBlobs:
            cv2.rectangle(gray, (b.rect[0], b.rect[1]), (b.rect[2], b.rect[3]), (0,0,0), 3)

        cv2.imshow('image', gray)
        rawCapture.truncate(0)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # cap.release()    
    cv2.destroyAllWindows()
    # im.show()


main()

from skimage.feature import blob_doh
import numpy as np
import cv2
import time

cap = cv2.VideoCapture(0)
numFrames = 120
repeat = 10
results = []

# Find timing for 10 iterations of 120 frames for DOH blob detection
for count in xrange(repeat):
    start = time.time()
    for i in xrange(numFrames):
        # Get frame from webcam
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Find blobs
        blobs = blob_doh(gray, max_sigma=30, threshold=.01)

        # Draw circles around blobs
        for blob in blobs:
            y, x, r = blob
            cv2.circle(gray, (int(x), int(y)), int(r), (0,0,255), 3)

    # Get timing
    end = time.time()
    seconds = end - start
    results.append(seconds)
    print "Finished iteration {0}...".format(count)

# Calculate results
totalSeconds = 0
totalFPS = 0
for result in results:
    totalSeconds += result
    totalFPS += numFrames / result

# Print results
avgSeconds = totalSeconds / repeat
avgFPS = totalFPS / repeat
print "----- Overall Result -----"
print "Average time taken: {0}".format(avgSeconds)
print "Average estimated fps: {0}".format(avgFPS)
print "--------------------"

cap.release()
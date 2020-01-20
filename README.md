# Motion Tracking DSLR for Automated Camerawork

This repo contains the project I developed and submitted for my 3rd year project at the University of Southampton.

## Structure
### ImageAnalysis
The computer vision aspect of the project, which analyses the video stream from the Raspberry Pi Camera to detect dark blobs. It then communicates how much to move to pan and tilt system to the local web server.
### PanTilt
The code that controls the servos which move the pan & tilt system itself. It receives commands serially from the web server running on the Rasberry Pi.
### Website
A relatively barebones interface to control the system manually or automated, and change its configuration. It receives the data from the image analysis side and processes it accordingly the then send the appropriate commands to the pan & tilt system. It also interacts with the connected DSLR camera to take pictures. Thumbnails of the images taken are displayed and can be selected to download.

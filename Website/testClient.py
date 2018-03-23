import zmq
import time
import random

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.RCVTIMEO = 1000
socket.connect("tcp://localhost:5555")

while True:
    try:
        message = socket.recv()
        print message
        socket.send(str(random.randint(0, 1000)))
    except Exception as e:
        print e

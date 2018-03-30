from flask import Flask
from flask import request
from flask import render_template
from flask import json
import zmq
import select
from time import sleep
import serial

# Web app
app = Flask(__name__)

# Stepper step amount when moving
PAN_STEP = "10"
TILT_STEP = "10"

# Setup interprocess communication with blob detector
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.RCVTIMEO = 1000
socket.bind("tcp://*:5555")

# Setup serial connection to pan/tilt controller
try:
    ser = serial.Serial('COM3', 115200, timeout=50, write_timeout=50)
    sleep(2)
    if ser.isOpen():
        print "Serial port is open..."
    else:
        print "Serial port is not open..."
        exit(1)
except serial.serialutil.SerialException as e:
    print "Failed to open serial port."


# Sends command over serial to pan/tilt controller
# command : Command to send
def cmd(command):
    print "Sending command: '" + command + "'..."
    ser.write(command + '\0')
    # sleep(0.1)


@app.route('/', methods=['POST', 'GET'])
def site():
    failed = False
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        # inputText = request.form['testinput']
        # socket.send_string(inputText)

        # try:
        #     message = socket.recv()
        # except Exception as e:
        #     print e

        # return message

        reqType = request.form['type']

        if reqType == "thumbnails":
            print "Getting thumbnails..."
            return "Thumbnails"
        elif reqType == "move":
            direction = request.form['direction']
            print "Attempting to move in direction " + direction + "..."
            if direction == 'left':
                cmd('PAN -' + PAN_STEP)
            elif direction == 'down':
                cmd('TILT -' + TILT_STEP)
            elif direction == 'up':
                cmd('TILT ' + TILT_STEP)
            elif direction == 'right':
                cmd('PAN ' + PAN_STEP)
            elif direction == 'reset':
                cmd('RESET')
            else:
                print "Unknown movement: " + direction
                failed = True
        elif reqType == "step":
            axis = request.form['amount'].encode('ascii')
            if request.form['axis'] == "pan":
                global PAN_STEP
                PAN_STEP = axis
            elif request.form['axis'] == "tilt":
                global TILT_STEP
                TILT_STEP = axis
        else:
            print "Unknown request type: " + request.form['type']
            failed = True
    else:
        print "Unsupported method: " + request.method
        failed = True

    if failed:
        return render_template('error.html')
    else:
        return "Success"

if __name__ == "__main__":
    cmd('MANUAL')
    app.run()

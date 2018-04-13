#!/usr/bin/python2

import threading
from flask import Flask
from flask import request
from flask import render_template
from flask import json
from flask.json import jsonify
import zmq
import select
from time import sleep
import serial
from subprocess import call
from datetime import datetime

# Pan/tilt connected port
PAN_TILT_PORT = "/dev/ttyUSB0"

LAST_PICTURE = datetime.now()

# Web app
app = Flask(__name__)

# Stepper step amount when moving
PAN_STEP = "10"
TILT_STEP = "10"

# Setup interprocess communication with blob detector
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:5555")

# Serial connection to pan/tilt
ser = None

# Setup serial connection to pan/tilt controller
def connectToSerial():
    global ser
    try:
        if ser is not None:
            ser.close()

        ser = serial.Serial(PAN_TILT_PORT, 115200, timeout=0.01, write_timeout=0.01)
        sleep(2)

        if ser.isOpen():
            print "Serial port is open..."
        else:
            print "Serial port is not open..."
            exit(1)
    except serial.serialutil.SerialException as e:
        print "Failed to open serial port."
        exit(1)

# Sends command over serial to pan/tilt controller
# command : Command to send
def cmd(command):
    print "Sending command: '" + command + "'..."
    try:
        ser.write(command.encode('ascii'))

        # Wait until received reply from arduino
        while ser.in_waiting == 0: pass

        # Read reply
        out = ''
        while ser.in_waiting > 0:
            out += str(ser.read(1))
        if out == "INVALID COMMAND":
            return None
        else:
            out = out.split('\n')
            if len(out) < 2:
                return None
            try:
                # Parse current (pan, tilt) values
                return (int(out[0].split(' ')[1]), int(out[1].split(' ')[1]))
            except ValueError:
                return None
    except SerialTimeoutException:
        return None


# Gets the new pan/tilt positons from the blob detector
def getPositions():
    global LAST_PICTURE
    photoThread = None
    while True:
        positions = socket.recv()
        panTilt = positions.split(',')
        print "Received positions: " + positions

        # If in position, take photots every 3 seconds
        if positions == "0,0" and (datetime.now() - LAST_PICTURE).total_seconds() > 4:
            LAST_PICTURE = datetime.now()
            if photoThread is not None:
                photoThread.join()
            photoThread = threading.Thread(target=call, args=(["/home/pi/3rdYearProject/ImageAnalysis/takePhotos.sh"],))
            photoThread.start()

        cmd('PT ' + panTilt[0] + 'x' + panTilt[1])
#         sleep(0.1)

@app.route('/', methods=['POST', 'GET'])
def site():
    failed = False
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        reqType = request.form['type']

        if reqType == "thumbnails":
            print "Getting thumbnails..."
            return "Thumbnails"
        elif reqType == "move":
            direction = request.form['direction']
            print "Attempting to move in direction " + direction + "..."
            if direction == 'left':
                positions = cmd('PAN -' + PAN_STEP)
                if positions is None:
                    return "False"
                return jsonify(pan=positions[0], tilt=positions[1])
            elif direction == 'down':
                positions = cmd('TILT -' + TILT_STEP)
                if positions is None:
                    return "False"
                return jsonify(pan=positions[0], tilt=positions[1])
            elif direction == 'up':
                positions = cmd('TILT ' + TILT_STEP)
                if positions is None:
                    return "False"
                return jsonify(pan=positions[0], tilt=positions[1])
            elif direction == 'right':
                positions = cmd('PAN ' + PAN_STEP)
                if positions is None:
                    return "False"
                return jsonify(pan=positions[0], tilt=positions[1])
            elif direction == 'zero':
                positions = cmd('ZERO')
                if positions is None:
                    return "False"
                return jsonify(pan=positions[0], tilt=positions[1])
            else:
                print "Unknown movement: " + direction
                failed = True
        elif reqType == "step":
            amount = request.form['amount'].encode('ascii')
            if request.form['axis'] == "pan":
                global PAN_STEP
                PAN_STEP = amount
            elif request.form['axis'] == "tilt":
                global TILT_STEP
                TILT_STEP = amount
        elif reqType == "speed":
            amount = request.form['amount'].encode('ascii') 
            axis = request.form['axis']
            if axis == "pan":
                cmd('PAN_SPEED ' + amount)
                return "True"
            elif axis == "tilt":
                cmd('TILT_SPEED ' + amount)
                return "True"
            else:
                failed = True
        elif reqType == "picture":
            print "Taking picture..."
            call(["/home/pi/3rdYearProject/ImageAnalysis/takePhotos.sh"])
        elif reqType == "command":
            command = request.form['cmd']
            if (command.startswith("PT ") or
                    command.startswith("PAN ") or
                    command.startswith("TILT ") or
                    command.startswith("SET_PAN ") or
                    command.startswith("SET_TILT ") or
                    command.startswith("PAN_SPEED") or
                    command.startswith("TILT_SPEED") or
                    command.startswith("RESET") or
                    command.startswith("RESET_PAN") or
                    command.startswith("RESET_TILT") or
                    command.startswith("DEMO")):
                positions = cmd(command)
                if positions is None:
                    return "False"
                return jsonify(pan=positions[0], tilt=positions[1])
            elif command.startswith("ZERO"):
                connectToSerial()
                return jsonify(pan=0, tilt=0)
            else:
                return "False"
        elif reqType == "manualToggle":
            socket.send_string("MANUAL_TOGGLE")
            return "True"
        elif reqType == "block":
            if request.form['value'] == "true":
                print "Setting blocking mode to manual..."
                cmd('BLOCK')
            else:
                print "Setting blocking mode to auto..."
                cmd('NON_BLOCK')
        elif reqType == "setPos":
            val = request.form['value']
            try:
                int(val)
                axis = request.form['axis']
                if axis == "pan":
                    print "Setting pan to position " + val + "..."
                    cmd('SET_PAN ' + val)
                elif axis == "tilt":
                    print "Setting tilt to position " + val + "..."
                    cmd('SET_TILT ' + val)
                else:
                    failed = True
            except ValueError:
                return "False"
        elif reqType == "reset":
            connectToSerial()
            return jsonify(pan=0, tilt=0)
        elif reqType == "demo":
            print "Toggling demonstration mode..."
            socket.send_string("DEMO_TOGGLE")
        else:
            print "Unknown request type: " + request.form['type']
            failed = True
    else:
        print "Unsupported method: " + request.method
        failed = True

    if failed:
        print "Failed."
        return render_template('error.html')
    else:
        return "True"

if __name__ == "__main__":
    connectToSerial()
    backgroundThread = threading.Thread(target=getPositions)
    backgroundThread.daemon = True
    backgroundThread.start()
    # cmd('MANUAL')
    app.run(host='0.0.0.0', port=80)

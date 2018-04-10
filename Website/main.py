from flask import Flask
from flask import request
from flask import render_template
from flask import json
from flask.json import jsonify
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
    ser = serial.Serial('COM3', 115200, timeout=0.01, write_timeout=0.01)
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
        try:
            # Parse current (pan, tilt) values
            return (int(out[0].split(' ')[1]), int(out[1].split(' ')[1]))
        except ValueError:
            return None

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
            elif direction == 'reset':
                positions = cmd('RESET')
                if positions is None:
                    return "False"
                return jsonify(pan=positions[0], tilt=positions[1])
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
        elif reqType == "picture":
            print "Taking picture..."
            pass
        elif reqType == "command":
            command = request.form['cmd']
            if (command.startswith("PT ") or 
                command.startswith("PAN ") or
                command.startswith("TILT ") or
                command.startswith("SET_PAN ") or
                command.startswith("SET_TILT ") or
                command.startswith("RESET") or
                command.startswith("RESET_PAN") or
                command.startswith("RESET_TILT") or
                command.startswith("DEMO")):
                positions = cmd(command)
                if positions is None:
                    return "False"
                return jsonify(pan=positions[0], tilt=positions[1])
            else:
                return "False"
        elif reqType == "block":
            if request.form['value'] == "true":
                print "Setting blocking mode to manual..."
                cmd('MANUAL')
            else:
                print "Setting blocking mode to auto..."
                cmd('AUTO')
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
        elif reqType == "demo":
            print "Toggling demonstration mode..."
            pass
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
    cmd('MANUAL')
    app.run()

from flask import Flask
from flask import request
from flask import render_template
from flask import json
import zmq
import select

app = Flask(__name__)
context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.RCVTIMEO = 1000
socket.bind("tcp://*:5555")


@app.route('/', methods=['POST', 'GET'])
def hello():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        inputText = request.form['testinput']
        socket.send_string(inputText)

        try:
            message = socket.recv()
        except Exception as e:
            print e

        return message


if __name__ == "__main__":
    app.run()

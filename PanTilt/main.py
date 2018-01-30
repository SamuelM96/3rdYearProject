#!/bin/python2

import time
import serial

print "Opening serial port..."
# ser = serial.Serial('/dev/ttyUSB0', 115200)
ser = serial.Serial('COM1', 115200)
time.sleep(2)
if ser.isOpen():
    print "Serial port is open..."
else:
    print "Serial port is not open..."
    exit(1)

def cmd(command):
    ser.write(command + '\0')
    print ser.writable()
    time.sleep(1)
    while ser.out_waiting > 0:
        pass
    # output = ''
    print ser.readline()
    # while ser.inWaiting() > 0:
    #     output += str(ser.read(1))
    # print output

if ser.inWaiting() > 0:
    print 'There is currently ' + str(ser.inWaiting()) + ' bytes in the buffer...'
    print 'Reading initial data:'

    out = ''
    while ser.inWaiting() > 0:
        out += str(ser.read(1))
    print out

print 'Executing commands...'
# cmd('$20=0')
# cmd('$21=0')
# cmd('$22=1')
# cmd('$25=500')
# cmd('$24=500')
# cmd('$5=0')
# cmd('$X')
# cmd('M119')
# cmd('G1 F30 X-2 Y-4')
# cmd('G28')
# cmd('G1 F30 X0 Y0')
cmd("PAN3");
cmd("PAN-3");

print 'Closing port...'
ser.close()

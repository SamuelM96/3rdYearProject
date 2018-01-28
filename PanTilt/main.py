#!/bin/python2

import time
import serial

print "Opening serial port..."
ser = serial.Serial('/dev/ttyUSB0', 115200)
# ser = serial.Serial('/dev/ttyUSB0', 250000)
time.sleep(2)
if ser.isOpen():
    print "Serial port is open..."
else:
    print "Serial port is not open..."
    exit(1)

def cmd(s):
    ser.write(s + '\r\n')
    print ser.writable()
    time.sleep(1)
    output = ''
    while ser.inWaiting() > 0:
        output += str(ser.read(1))
    print output

print 'There is currently ' + str(ser.inWaiting()) + ' bytes in the buffer...'
print 'Reading initial data:'

o = ''
while ser.inWaiting() > 0:
    o += str(ser.read(1))
print o

print 'Executing commands...'
# cmd('$20=0')
cmd('$21=0')
# cmd('$22=1')
# cmd('$25=500')
# cmd('$24=500')
# cmd('$5=0')
cmd('$X')
# cmd('M119')
cmd('G1 F30 X-2 Y-4')
# cmd('G28')
cmd('G1 F30 X0 Y0')

print 'Closing port...'
ser.close()

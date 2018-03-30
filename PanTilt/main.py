from time import sleep
import serial

print "Opening serial port..."
ser = serial.Serial('COM3', 115200, timeout=50, write_timeout=50)
sleep(2)
if ser.isOpen():
    print "Serial port is open..."
else:
    print "Serial port is not open..."
    exit(1)

def cmd(command):
    ser.write(command + '\0')
    sleep(0.01)

if ser.inWaiting() > 0:
    print 'There is currently ' + str(ser.inWaiting()) + ' bytes in the buffer...'
    print 'Reading initial data:'

    out = ''
    while ser.inWaiting() > 0:
        out += str(ser.read(1))
    print out

print 'Executing commands...'
for x in xrange(0, 300, 1): 
    cmd("PT" + str(x) + "x0");

for x in xrange(300, 0, -1):
    cmd("PT" + str(x) + "x0")

print 'Closing port...'
ser.close()

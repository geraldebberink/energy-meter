import serial
import time
import sys


#dsrdtr should be set to one to suppress the automatic reset of the Arduino Diecimila
ser=serial.Serial('/dev/ttyUSB0',9600, timeout=5, dsrdtr=1)
print 'connected to: ' + ser.portstr

test=["0","0","0"]
line=""
reset=False
power=0.0
energyWh=0
for num in range(1,5):
    oldWh = energyWh
    ser.write("data?\n")
    ser.flush()
    line = ser.readline()
    test = line.split()
    reset = bool(int(test[0]))
    power = float(test[1])           
    energyWh = int(test[2])
    if reset:
        energyWh += oldWh
        ser.write("set "+str(energyWh))
        ser.flush()
    print int(time.time())
    print "reset: " + str(reset)
    print "current power usage: " + str(power)
    print "current energy Wh: " + str(energyWh)

    sys.stdout.flush()    
    time.sleep(10)
ser.close()
   


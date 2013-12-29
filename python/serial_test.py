import serial
import time
import sys


#dsrdtr should be set to zero to suppress the automatic reset of the Arduino Diecimila
ser=serial.Serial('/dev/ttyUSB0',9600, timeout=5, dsrdtr=1)
print 'connected to: ' + ser.portstr

test=[ ]
line=""
reset=False
power=0.0
energyWh=0
ser.flush()
for num in range(1,5):
    oldWh = energyWh
    ser.write("data?\n")
    ser.flush()
    line = ser.readline()
    test = line.split()
    if(len(test)==0):
            print("zero input")
    elif(len(test)==1):
        reset = bool(int(test[0]))
    elif(len(test)==2):
        reset = bool(int(test[0]))
        power = float(test[1])
    elif(len(test)==3):
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
   


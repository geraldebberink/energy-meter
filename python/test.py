import serial
import time
from pyrrd import rrd
import os
import tempfile


filename='/home/gerald/energy_meter/test.rrd'
if not(os.path.isfile(filename)):
    cfs = ['AVERAGE','MAX']
    temp = [[1,120], [15,92],[60,148],[180,248],[840,732],[1680,1098],[11760,780]]
    dataSources = []
    roundRobinArchives = []
    dataSource = rrd.DataSource( dsName='power', dsType='GAUGE', heartbeat='120')
    dataSources.append(dataSource)
    dataSource = rrd.DataSource( dsName='Energy', dsType='COUNTER', heartbeat='120')
    dataSources.append(dataSource)
    for val in cfs:
        for val2 in temp:
            roundRobinDatabase=rrd.RRA(cf=val, xff=0.5, steps=val2[0], rows=val2[1])
            roundRobinArchives.append(roundRobinDatabase)
    myRRD = rrd.RRD(filename, ds=dataSources, rra=roundRobinArchives, start=(int(time.time())-86400), step=60)
    myRRD.create()

else:
    myRRD = rrd.RRD(filename, mode='r')
    
test=[]
line=""
reset=False
power=0.0
energyWh=0
ser=serial.Serial('/dev/ttyUSB0',9600, timeout=30)
print 'connected to: ' + ser.portstr

for num in range(1,21):
    ser.write("data?\r\n")
    time.sleep(0.01)
    line = ser.readline()
    test = line.split(",")
    reset = bool(test[1])
    power = float(test[0])
    #energyWh = int(test[1])
    print "current power usage: " + str(power)
    print "current energy Wh: " + str(energyWh)
    
    myRRD.bufferValue(str(int(time.time())), str(int(power)), str(energyWh))
    myRRD.update()
    time.sleep(60)
ser.close()
   


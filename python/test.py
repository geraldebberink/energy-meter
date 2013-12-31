import arduinoserial.arduinoserial as serial
import time
from pyrrd import rrd
import os
import tempfile

serDevice='/dev/ttyUSB0'
filename='/home/gerald/energy_meter/test.rrd'
pulseFile='/home/gerald/energy_meter/pulse_file.pf' 

minute = 1
quarter = 15* minute
hour = 4 * quarter
day = 24 * hour
week = 7 * hour
month = day * 30
year = 365 * day


if not(os.path.isfile(filename)):
    cfs = ['AVERAGE','MAX']
    temp = [[minute,2*hour], [quarter,day/quarter],[hour,week/hour],[3*hour,month/(3*hour)],[day / 2, year/(day/2)],[day,(3*year)/day],[week,(15*year)/week]]
    dataSources = []
    roundRobinArchives = []
    dataSource = rrd.DataSource( dsName='power', dsType='GAUGE', heartbeat='120')
    dataSources.append(dataSource)
    dataSource = rrd.DataSource( dsName='energy', dsType='COUNTER', heartbeat='120')
    dataSources.append(dataSource)
    for val in cfs:
        for val2 in temp:
            roundRobinDatabase=rrd.RRA(cf=val, xff=0.5, steps=val2[0], rows=val2[1])
            roundRobinArchives.append(roundRobinDatabase)
    myRRD = rrd.RRD(filename, ds=dataSources, rra=roundRobinArchives, start=(int(time.time())-86400), step=60)
    myRRD.create()

else:
    myRRD = rrd.RRD(filename, mode='r')

#open the pulseFile
f = open(pulseFile, 'r')
oldWh= int(f.readline())
f.close()
    
#dsrdtr should be set to zero to suppress the automatic reset of the Arduino Diecimila
ser=serial.SerialPort(serDevice,9600)

test=[ ]
line=""
reset=False
power=0.0
energyWh=0
time.sleep(2)
ser.write("data?\n")
time.sleep(2)
line = ser.read_until('\n')
test = line.split()

#if data is read and no reset has occured insert data in database
if(len(test)==3):
    reset = bool(int(test[0]))
    power = float(test[1])
    energyWh = int(test[2])
    if reset:
        energyWh += oldWh
        ser.write("set "+str(energyWh)+"\n")
	time.sleep(2)
    else:    
        myRRD.bufferValue(str(int(time.time())), str(int(power)), str(energyWh))
        myRRD.update()
        f = open(pulseFile, 'w')
        s = str(energyWh)
        f.write(s)
        f.close()

   


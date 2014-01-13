import time
import os
import ConfigParser as configparser

from pyrrd import rrd
import arduinoserial.arduinoserial as serial

# try to locate a ini file in these place and use that to find the rest of 
# settings. 
possible_paths = ('/etc/defaults', os.path.expanduser('~/.energy_meter'), '.')

# set the defaults for the configuration, so that if we miss a setting in the
# file we have a "save" default.
config = configparser.SaveConfigParser({
          'serial_device': '/dev/ttyUSB0',
          'program_root': '/home/gerald/energy_meter/', 
          'rrd_file': 'test.rrd', 
          'pulse_file': 'pulse_file.pf',
          'html_root': '/var/www/energy'})

# locate a file and read the settings.
for path in possible_paths:
    configfile = path + '/home_config.ini'
    if os.path.isfile(configfile):
        config.read(configfile)
        serial_device = config.get('hardware', 'serial_device')
        program_root = config.get('files', 'program_root')
        rrd_file = config.get('files', 'rrd_file')
        pulse_file = config.get('files', 'pulse_file')
        html_root = config.get('files', 'html_root')

# create the filenames        
filename = program_root + rrd_file
pulsefile = program_root + pulse_file 

# create the different time values
minute = 1
quarter = 15 * minute
hour = 4 * quarter
day = 24 * hour
week = 7 * hour
month = day * 30
year = 365 * day

# if no rrd file is there create a database with the following parameters.
if not(os.path.isfile(filename)):
    cfs = ['AVERAGE','MAX']
    times = [[minute,2*hour], [quarter,day/quarter],[hour,week/hour],[3*hour,month/(3*hour)],[day / 2, year/(day/2)],[day,(3*year)/day],[week,(15*year)/week]]
    dataSources = []
    roundRobinArchives = []
    dataSource = rrd.DataSource( dsName='power', dsType='GAUGE', heartbeat='120')
    dataSources.append(dataSource)
    dataSource = rrd.DataSource( dsName='energy', dsType='COUNTER', heartbeat='120')
    dataSources.append(dataSource)
    for val in cfs:
        for val2 in times:
            roundRobinDatabase=rrd.RRA(cf=val, xff=0.5, steps=val2[0], rows=val2[1])
            roundRobinArchives.append(roundRobinDatabase)
    myRRD = rrd.RRD(filename, ds=dataSources, rra=roundRobinArchives, start=(int(time.time())-86400), step=60)
    myRRD.create()

else:
    myRRD = rrd.RRD(filename, mode='r')

# open the pulsefile and put the value in the oldWh
f = open(pulsefile, 'r')
oldWh= int(f.readline())
f.close()
    
# open the serial port and wait two seconds
# dsrdtr should be set to zero to suppress the automatic reset 
# of the Arduino Diecimila. 
ser=serial.SerialPort(serial_device,9600)
time.sleep(2)


# set default values.
test=[ ]
line=""
reset=False
power=0.0
energyWh=0

# ask the data and split it to the columns
ser.write("data?\n")
time.sleep(2)
line = ser.read_until('\n')
test = line.split()

# if data is read and no reset has occured insert data in database
# after reset the old and new energy are added and then write it back to
# the arduino
# if no reset is given save the current power in the pulse file
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
        f = open(pulsefile, 'w')
        s = str(energyWh)
        f.write(s)
        f.close()
import serial
import time
from pyrrd import rrd
import os
import tempfile

minute = 1
quarter = 15* minute
hour = 4 * quarter
day = 24 * hour
week = 7 * day
month = day * 30
year = 365 * day


filename='/home/gerald/energy_meter/test.rrd'
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
    myRRD.info()

else:
    myRRD = rrd.RRD(filename, mode='r')
    myRRD.info()

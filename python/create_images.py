import serial
import time
from pyrrd import rrd
from pyrrd.graph import CDEF, DEF, AREA, VDEF, LINE, GPRINT, Graph, ColorAttributes
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
graphfile='/home/gerald/energy_meter/test' 
myRRD = rrd.RRD(filename, mode='r')
temp = [[2*hour,'two_hour'], [day,'last_day'], [week,'last_week'], [month,'last_month'], [year,'last_year'], [3*year,'last_three_years'], [15*year,'last_decade']]


ca = ColorAttributes()
ca.back = '#333333'
ca.canvas = '#333333'
ca.shadea = '#000000'
ca.shadeb = '#111111'
ca.mgrid = '#CCCCCC'
ca.axis = '#FFFFFF'
ca.frame = '#AAAAAA'
ca.font = '#FFFFFF'
ca.arrow = '#FFFFFF'

currentTime = int(time.time())

def1 = DEF(rrdfile=myRRD.filename, vname='Watt', dsName='power')
def2 = DEF(rrdfile=myRRD.filename, vname='Wh', dsName='energy')
vdef1 = VDEF(vname='maxpower', rpn='%s,MAXIMUM' % def1.vname)
vdef2 = VDEF(vname='avgpower', rpn='%s,AVERAGE' % def1.vname)
vdef3 = VDEF(vname='maxenergy', rpn='%s,MAXIMUM' % def2.vname)
cdef1 = CDEF(vname='Joule', rpn='%s,3600,*' % def2.vname) 

area1 = AREA(defObj=def1, color='#006600', legend='Our Power')
area2 = AREA(defObj=cdef1, color='#006600', legend='Our Energy')
line1 = LINE(defObj=vdef1, color='#660000', legend='Our Maximum')
line2 = LINE(defObj=vdef2, color='#009900', legend='Our Average')

gprint1 = GPRINT(vdef2,'average power %6.2lf watt')
gprint2 = GPRINT(vdef1,'maximum power %6.2lf watt')


labels = [['power\ in\ Watt',[def1, vdef1, vdef2, area1, gprint1, gprint2, line1, line2]],['energy\ in\ Joule',[def2,cdef1,  area2]]]


for num in range(0,len(labels)): 
    for val in temp: 
        g = Graph((graphfile+'_'+labels[num][0].split('\ ',1)[0]+'_'+val[1]+'.png'), start=(currentTime-(val[0]*60)), end=currentTime, vertical_label=labels[num][0], color=ca, imgformat='png')
        g.data.extend(labels[num][1])
        g.write()

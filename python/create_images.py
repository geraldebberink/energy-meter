import serial
import time
from pyrrd import rrd
from pyrrd.graph import DEF, CDEF, LINE, Graph, ColorAttributes
import os
import tempfile

filename='/home/gerald/energy_meter/test.rrd'
graphfile='/home/gerald/energy_meter/test.png' 
myRRD = rrd.RRD(filename, mode='r')

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


def1 = DEF(rrdfile=myRRD.filename, vname='Watt', dsName='power')
def2 = DEF(rrdfile=myRRD.filename, vname='Joule', dsName='energy')
cdef1 = CDEF(vname='kWatt', rpn='%s,1000,/' %def1.vname)
line1 = LINE(defObj=def1, color='#009900')
line2 = LINE(defObj=def2, color='#990000')
g = Graph(graphfile, start=(int(time.time())-86400), end=(int(time.time())+86400), vertical_label='power', color=ca, imgformat='png')
g.data.extend([def1,def2, line1, line2])
g.write(debug=True)

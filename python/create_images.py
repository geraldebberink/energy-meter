import time
import os

from pyrrd import rrd
from pyrrd.graph import CDEF, DEF, AREA, VDEF, LINE, GPRINT, Graph, ColorAttributes
import ConfigParser as configparser

# try to locate a ini file in these place and use that to find the rest of 
# settings. 
possible_paths = ('/etc/defaults', os.path.expanduser('~/.energy_meter'), '.')

# set the defaults for the configuration, so that if we miss a setting in the
# file we have a "save" default.
config = configparser.SafeConfigParser({
          'program_root': '/home/gerald/energy_meter/',
          'rrd_file': 'test.rrd',
          'pulse_file': 'pulse_file.pf',
          'html_root': '/var/www/energy'})

# locate a file and read the settings.
for path in possible_paths:
    configfile = path + '/home_config.ini'
    if os.path.isfile(configfile):
        config.read(configfile)
        program_root = config.get('files', 'program_root')
        rrd_file = config.get('files', 'rrd_file')
        pulse_file = config.get('files', 'pulse_file')
        html_root = config.get('files', 'html_root')
print 'config file used: ' + configfile
        
minute = 1
quarter = 15* minute
hour = 4 * quarter
day = 24 * hour
week = 7 * day
month = day * 30
year = 365 * day


rrdfile=program_root + rrd_file
graphfile=html_root +'/test'
myRRD = rrd.RRD(rrdfile, mode='r')
times = [[2*hour,'two_hour'], [day,'last_day'], 
        [week,'last_week'], [month,'last_month'], 
        [year,'last_year'], [3*year,'last_three_years'], 
        [15*year,'last_decade']]


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

gprint1 = GPRINT(vdef2,'average power %6.0lf watt')
gprint2 = GPRINT(vdef1,'maximum power %6.0lf watt')

# setup the labels and definitions also setup the different file sizes
labels = ['power\ in\ Watt','energy\ in\ Joule']
definitions = [[def1, vdef1, vdef2, area1, gprint1, gprint2, line1, line2],[def2,cdef1, area2]]
sizes = [[[497,169],'small'],[[800,600],'large']]

#setup a dummpy image
g = Graph('dummpy.png', end=currentTime, color=ca, imgformat='png')

for num in range(0,len(labels)):
    g.vertical_label = labels[num]
    g.data = definitions[num]
    
    for t in times:
        g.start = (currentTime - (t[0] * 60))
        
        for size in sizes:
            g.width = size[0][0]
            g.height =  size[0][1]
            g.filename = graphfile+'_%s_%s_%s.png' % ( 
                                                labels[num].split('\ ',1)[0], 
                                                t[1], size[1] )
            g.write(debug=False)
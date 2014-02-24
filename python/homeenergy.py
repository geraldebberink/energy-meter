import time
import os
import shutil
import ConfigParser as configparser
import arduinoserial.arduinoserial as serial

if __name__ == "__main__":
    try:
        import daemoncxt.runner as runner
    except ImportError:
        import daemon.runner as runner

from pyrrd import rrd
from pyrrd.graph import (CDEF, DEF, AREA, VDEF, LINE, 
                                GPRINT, Graph, ColorAttributes)

class HomeEnergy:
    minute = 1
    quarter = 15* minute
    hour = 4 * quarter
    day = 24 * hour
    week = 7 * day
    month = day * 30
    year = 365 * day

    def __init__(self):
        """Testing this"""
        self.possible_paths = ('/etc/default', 
                                os.path.expanduser('~/.energy_meter'), '.')
        self.program_root = '/home/gerald/energy_meter/'
        self.rrd_file = 'test.rrd'
        self.pulse_file = 'pulse_file.pf'
        self.html_root = '/var/www/energy/test_'
        self.maximum_power = 8200
        self.user = 'test'
        self.serial_device = '/dev/ttyUSB0'
        self.sizes = [[[497,169],'small'],[[1280,720],'large']]
        self.times = [[2*self.day,'two_day'], 
                        [self.week,'last_week'], 
                        [self.month,'last_month'], 
                        [self.year,'last_year'], 
                        [15*self.year,'last_decade']]
        self.colors = ColorAttributes()
        self.colors.back = '#333333'
        self.colors.canvas = '#333333'
        self.colors.shadea = '#000000'
        self.colors.shadeb = '#111111'
        self.colors.mgrid = '#CCCCCC'
        self.colors.axis = '#FFFFFF'
        self.colors.frame = '#AAAAAA'
        self.colors.font = '#FFFFFF'
        self.colors.arrow = '#FFFFFF'
        self.updates = 4
        # derived values
        self.rrdfile = self.program_root + self.rrd_file
	self.pulsefile = self.program_root + self.pulse_file
        self.update_interval = 60 / self.updates
	
	# needed for daemon.runner 
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/homeenergy.pid'
        self.pidfile_timeout = 5
        
    def loadconfig(self):
        # try to locate a ini file in these place and use that to find the 
        # rest of settings. 
        
        # set the defaults for the configuration, so that if we miss a setting
        # in the file we have a "save" default.
        config = configparser.SafeConfigParser({
                    'program_root': '/home/gerald/energy_meter/',
                    'rrd_file': 'test.rrd',
                    'pulse_file': 'pulse_file.pf',
                    'html_root': '/var/www/energy',
                    'maximum_power': 8200})   
          
        # locate a file and read the settings.
        for path in self.possible_paths:
            configfile = path + '/home_config.ini'
            if os.path.isfile(configfile):
                config.read(configfile)
                # program variables
                self.program_root = config.get('files', 'program_root')
                self.rrd_file = config.get('files', 'rrd_file')
                self.pulse_file = config.get('files', 'pulse_file')
                self.html_root = config.get('files', 'html_root')
                self.maximum_power = config.getint('settings', 'maximum_power')
                self.updates = config.getint('settings', 'updates')
                self.user = config.get('settings', 'user')
                # derived variables
                self.update_interval = 60 / self.updates
                self.rrdfile = self.program_root + self.rrd_file
		self.pulsefile = self.program_root + self.pulse_file
                # color variables
                self.colors.back = config.get('colors', 'back')
                self.colors.canvas = config.get('colors','canvas')
                self.colors.shadea = config.get('colors','shadea')
                self.colors.shadeb = config.get('colors','shadeb')
                self.colors.mgrid = config.get('colors','mgrid')
                self.colors.axis = config.get('colors','axis')
                self.colors.frame = config.get('colors','frame')
                self.colors.font = config.get('colors','font')
                self.colors.arrow = config.get('colors','arrow')
                # hardware variables
                self.serial_device = config.get('hardware', 'serial_interface')


                
    def createimages(self, currentTime=None):
        if currentTime is None:
            currentTime = int(time.time())
        
        if os.path.isfile(self.rrdfile):
            myRRD = rrd.RRD(self.rrdfile, mode='r')
                    
            def1 = DEF(rrdfile=myRRD.filename, vname='Wh', dsName='energy')
            vdef1 = VDEF(vname='maxpower', rpn='%s,MAXIMUM' % def1.vname)
            vdef2 = VDEF(vname='avgpower', rpn='%s,AVERAGE' % def1.vname)
            cdef1 = CDEF(vname='Joule', rpn='%s,3600,*' % def1.vname) 
            
            area1 = AREA(defObj=cdef1, color='#006600', legend='Energy usage')
            line1 = LINE(defObj=vdef1, color='#660000', legend='Maximum usage')
            line2 = LINE(defObj=vdef2, color='#009900', legend='Average usage')
            
            gprint1 = GPRINT(vdef2,'average power %5.0lf watt')
            gprint2 = GPRINT(vdef1,'maximum power %5.0lf watt')
            
            # setup the labels and definitions also setup 
            # the different file sizes
            labels = ['Energy used in Joule']
            definitions = [
                [def1, vdef1, vdef2, cdef1, area1, gprint1, gprint2, line1, line2]]
            
            #setup a dummpy image
            g = Graph('dummpy.png', end=currentTime, color=self.colors, 
                                    imgformat='png')
            
            for num in range(0, len(labels)):
                g.vertical_label = labels[num]
                g.data = definitions[num]
                
                for t in self.times:
                    g.start = (currentTime - (t[0] * 60))
                    
                    for size in self.sizes:
                        g.width = size[0][0]
                        g.height =  size[0][1]
                        g.filename = self.html_root+'%s_%s_%s.png' % ( 
                                            labels[num].split('\ ',1)[0], 
                                            t[1], size[1] )
                        g.write(debug=False)
        
    def createdatabase(self, rrdfile=None):
        if rrdfile is None:
            rrdfile = self.rrdfile           
        if os.path.isfile(rrdfile):
            shutil.copy(rrdfile, (rrdfile[0:-4]+'.bak'))
        cfs = ['AVERAGE','MAX']
        times = [[self.minute, (2*self.day)/self.minute], 
                [self.quarter, self.week/self.quarter],
                [self.hour, self.month/self.hour],
                [self.hour, self.year/self.hour],
                [self.day,(15*self.year)/self.day],
                ]
        dataSources = []
        roundRobinArchives = []
        dataSource = rrd.DataSource( dsName='power', dsType='GAUGE', 
                                    heartbeat='120')
        dataSources.append(dataSource)
        dataSource = rrd.DataSource( dsName='energy', dsType='COUNTER', 
                                    heartbeat='120')
        dataSources.append(dataSource)
        for val in cfs:
            for val2 in times:
                roundRobinDatabase=rrd.RRA(cf=val, xff=0.5, 
                                    steps=val2[0], rows=val2[1])
                roundRobinArchives.append(roundRobinDatabase)
        myRRD = rrd.RRD(rrdfile, ds=dataSources, rra=roundRobinArchives, 
                                    start=(int(time.time())-86400), step=60)
        myRRD.create()
        
    def readcontroller(self, rrdfile=None):
        if rrdfile is None:
            rrdfile = self.rrdfile
        if not(os.path.isfile(rrdfile)):
            self.createdatabase(rrdfile)
        # open the pulsefile and put the value in the oldWh
        myRRD = rrd.RRD(self.rrdfile, mode='r')
        f = open(self.pulsefile, 'r')
        oldWh = int(f.readline())
        f.close()
            
        # open the serial port and wait two seconds
        # dsrdtr should be set to zero to suppress the automatic reset 
        # of the Arduino Diecimila. 
        ser = serial.SerialPort(self.serial_device,9600)
        time.sleep(2)
        
        # set default values.
        test = [ ]
        line = ""
        reset = False
        power = 0.0
        energyWh = 0
        
        currTime = time.time()
        
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
                ser.write("set " + str(energyWh) + "\n")
       	    	time.sleep(2)
            else:
                if (power > self.maximum_power):
                     myRRD.bufferValue(str(int(currTime)), 'U', 'U')
                else:    
                     myRRD.bufferValue(str(int(time.time())), str(int(power)), 
                                        str(energyWh))
            myRRD.update()
            f = open( self.pulsefile, 'w')
            s = str( energyWh )
            f.write(s)
            f.close()
            
    def run(self):
        while True:
            self.readcontroller()
            if (time.struct_time(time.gmtime()).tm_min%self.update_interval == 0):
                self.createimages()
            time.sleep(60)
if __name__ == "__main__":
    energy = HomeEnergy()
    energy.loadconfig()
    
    daemon_runner = runner.DaemonRunner(energy)
    daemon_runner.do_action()

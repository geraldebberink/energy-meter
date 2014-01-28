energy-meter
============
This is a small energy meter project.
It consists of an arduio sketch to run on a Arduino Diecimila.
This is used to count pulses from an Home energy-meter with an S-interface found in many homes. Alternatively you could use an extra.
And then communicates via a virtual serial port with a python script.

The results are stored in an round robin database.

Currently this is a work in progress with many unknowns and firsts.

* It is the first time I really program an Arduino to do something usefull.
* It is the first time i use python as a programming language to do anything.
* ~~It is unknown if the S interface on my ENTES ES-32L works with 5V (it should though)~~ The ENTES ES-32L _IS_ compatible

For more information see:
http://blog.ebberink.nl//topics/11-electronics/home-energy-meter

Installation
============

Load the sketch to your arduino. 
copy the file home_config.ini
and edit the appropiate variables.


Arduino sketch
=============

The arduino sketch is designed to be interrupted when a pulse is there. It then adds this pulse to the ones already there.
In the mean time the serial interface is monitored. When a newline is encounterd the loop checks if the command set is given. If not it gives the three values back.

return values
-------------
The values are in order:
1. Reset has occured
2. current power usage in W
3. Total power used in Wh

set command
-----------
When the command string starts with set the system will take the following integer and populate the nPulses variable with that.
It is mainly after a reset since the arduino stores the value in volitale memory.

TO DO
-----
- [x] make the interrupt work well

python interface
================
The python interface exists of a single file which can be used both as a module for integration in an other program or as a daemon directly useing some defaults and other values from the ini file.


TO DO
-----
- [X] create test software to check workings of communication
- [X] make use of config files.
- [X] create deamon
- [X] create nice graphs
- [ ] create a nice way to display the graphs
- [X] rename files to usefull names: test.py is *not* a usefull name
- [X] create usefull comments
- [X] give variables discriptive names: num is *not* descriptive

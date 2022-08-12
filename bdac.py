#!/usr/bin/python3

# bdac - Bafang display and config
# Copyright (C) 2022  George Farris - VE7FRG

# bdac can be used to configure the controller in a Bafang BBS02 motor.
# You can change parameters, read and write config files (.bdac) to
# your computer and print human readable reports to a file.
# It has only been tested on the Bafang BSS02 controller.

# Usage:
#   bdac                     Normal use, must have serial connection established.
#   bdac --help              Print this help.
#   bdac --report            Retrieve controller settings and print report.
#   bdac --report <filename> Retrieve settings from file and report.
#   bdac --test              Run bdac with test data.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Footer

# v1.5 - 2022/08/03 - Changed dictionaires to OrderedDict 
# v1.6 - 2022/08/08 - Added --test command line argument
#                     Added save to a time stamped file in writing flash
#                     Added "View Report" to menu - human readable configs
#                     Added time stamped comms log file (bdac.log)  
#                     Show which controller areas are being read
# v1.7 - 2022/08/09 - Added ability to run report from file on command line
# v1.7.2            - Fix bug on time stamp file save.

import os
import sys
import json
import time
import curses
import datetime
sys.path.append('/usr/local/share/bdac')
from bdac_gui import BdacTerm
from time import sleep
from serial import Serial, SerialException
from collections import OrderedDict
from binascii import hexlify

VERSION = 'V1.7.2 - Python 3'
VERSION_DATE = 'Aug 9, 2022'

PORT = '/dev/ttyUSB0'

# Config commands
INFO_CMD = b'\x11\x51\x04\xb0\x05'
BASIC_CMD = b'\x11\x52'
PAS_CMD = b'\x11\x53'
THROTTLE_CMD = b'\x11\x54'
# Status commands
SPEED_CMD = b'\x11\x20'             # return 3 bytes
STATUS_CMD = b'\x11\x08'            # return 01 = normal, 03 = braking, 21 = speed sensor error
POWER_CMD = b'\x11\x0a'             # return xxxx = Watts, 0=W,1=checksum+0
BATTERY_CMD = b'\x11\x11'           # return xxxx = V, 0=Battery_Percent,1=checksum+0

#-----------------------------------------------------------------------
# DICTIONARIES
#-----------------------------------------------------------------------
# dictionaries for BASIC, PAS and THROTTLE
basic_dict = OrderedDict()
pas_dict = OrderedDict()
throttle_dict = OrderedDict()

# Wheel diameters Tis is for display purposes and is not used yet
wd_dict = OrderedDict()
wd_dict = {0x20:16,0x22:17,0x24:18,0x26:19,0x28:20,0x30:21,0x2B:22,0x2D:23,
      0x2F:24,0x32:25,0x34:26,0x35:27,0x37:'700C',0x38:28,0x3A:29,0x3C:30}

# Pedal Sensor Type
pst_dict = OrderedDict()
pst_dict = {0x00:'None',0x01:'DH-Sensor-12',0x02:'BB-Sensor-32',0x03:'DoubleSignal-24'}

# Designated Assist in THROTTLE section
dat_dict = OrderedDict()
dat_dict = {0x00:'MODE_0',0x01:'MODE_1',0x02:'MODE_1',0x03:'MODE_3',0x04:'MODE_4',0x05:'MODE_5',
        0x06:'MODE_6',0x07:'MODE_7',0x08:'MODE_8',0x09:'MODE_9',0xFF:'DISPLAY'}

#-----------------------------------------------------------------------
# write command to controller and read response
#-----------------------------------------------------------------------
def read_config(cm):
    # using with open allows us to not worry about closing the file if we so choose
    with open("bdac.log", mode='a') as f:
        t = time.localtime()
        stamp = time.strftime('%Y%m%d_%H%M%S', t)
        f.write("{0} -> {1}\n".format(stamp, hexlify(cm,',',1)))
        ser.write(cm)
        ser.flush()
        sleep(1)
        resp = ser.read(100)
        f.write("{0} <- {1}\n".format(stamp, hexlify(resp,',',1)))
        f.close()
        return resp

#-----------------------------------------------------------------------
# Get INFO config (b'\x11\x51\x04\xb0\x05')
#-----------------------------------------------------------------------
# Controller responds with 19 bytes
# Byte[0]     - Command [\x51]
# Byte[1]     - Response length
# Byte[2-5]   - Manufacturer - ASCII
# Byte[6-9]   - Model - ASCII
# Byte[10-11] - HW-Version - ASCII
# Byte[12-15] - FW-Version - ASCII
# Byte[16]    - Voltage {0:24,1:36'2:48,3:60,4:24_48,5:24-60}
# Byte[17]    - Maximum current in amps
# Byte[18]    - Checksum - no one cares
def get_info_config():
    volts_list = [24,36,48,60]
    if test_data:
        resp = b'\x51\x10\x48\x5a\x58\x54\x53\x5a\x5a\x39\x31\x31\x32\x30\x31\x31\x02\x19\x22'
    else:
        resp = read_config(INFO_CMD)
    # convert bytes 2-15 to ascii list
    l = [20,20] # make l the same index as resp
    for i in range(2, len(resp)-3): #start loop at 3rd byte
        l.append(chr(resp[i]))
    print('Manufacturer:   -> {0:s}{1:s}{2:s}{3:s}'.format(l[2],l[3],l[4],l[5]))
    print('Model:          -> {0:s}{1:s}{2:s}{3:s}'.format(l[6],l[7],l[8],l[9]))
    print('Hardware-Ver    -> V{0:s}.{1:s}'.format(l[10],l[11]))
    print('Firmware-Ver:   -> V{0:s}.{1:s}.{2:s}.{3:s}'.format(l[12],l[13],l[14],l[15]))
    print('Voltage:        -> {0}V'.format(int( volts_list[resp[16]])))
    print('Max Current:    -> {0}A'.format(int(resp[17])))

#-----------------------------------------------------------------------
# Get BASIC config (b'\x11\x52')
#-----------------------------------------------------------------------
# Controller responds with 27 bytes
# Byte[0]     - Command [\x52]
# Byte[1]     - Response length
# Byte[2]     - LBP,         Low Battery Protect, int
# Byte[3]     - LC,          Limit Current, int
# Byte[4-13]  - ALC0-ALC9,   Asist Level Current Limit,
# Byte[14-23] - ALBP0-ALBP9, Assit Level Speed Limit in %
# Byte[24]    - WD,          Wheel Diameter * 2 - list
# Byte[25]    - SMM,SMS      Speedometer Model and Speed signals, bit field see below
# Byte[26]    - Checksum - no one cares

# Speedmeter_Model last 2 bits of resp[25]
#  EXTERNAL = 0b00,     
#  INTERNAL = 0b01,
#  MOTORPHASE = 0b10
# Speed Signals per wheel revolution, lowest 6 bits of resp[25]
def get_basic_config():
    if test_data:
        resp = b'\x52\x18\x29\x0f\x00\x34\x3a\x40\x46\x4c\x52\x58\x5e\x64\x00\x24\x2c\x34\x3c\x44\x4c\x54\x5c\x64\x38\x01\xd5'
    else:
        resp = read_config(BASIC_CMD)
    
    basic_dict['LBP'] = [resp[2], 'Low battery protection, voltage where the motor will quit']
    basic_dict['LC'] = [resp[3], 'Current limit, Maximum current allowed to flow to motor']

    basic_dict['ALC0'] = [resp[4], 'Assist level 0 current setting in percent']
    basic_dict['ALC1'] = [resp[5], 'Assist level 1 current setting in percent']
    basic_dict['ALC2'] = [resp[6], 'Assist level 2 current setting in percent']
    basic_dict['ALC3'] = [resp[7], 'Assist level 3 current setting in percent']
    basic_dict['ALC4'] = [resp[8], 'Assist level 4 current setting in percent']
    basic_dict['ALC5'] = [resp[9], 'Assist level 5 current setting in percent']
    basic_dict['ALC6'] = [resp[10], 'Assist level 6 current setting in percent']
    basic_dict['ALC7'] = [resp[11], 'Assist level 7 current setting in percent']
    basic_dict['ALC8'] = [resp[12], 'Assist level 8 current setting in percent']
    basic_dict['ALC9'] = [resp[13], 'Assist level 9 current setting in percent']

    basic_dict['ALSL0'] = [resp[14], 'Assist level 0 speed limit percentage']
    basic_dict['ALSL1'] = [resp[15], 'Assist level 1 speed limit percentage']
    basic_dict['ALSL2'] = [resp[16], 'Assist level 2 speed limit percentage']
    basic_dict['ALSL3'] = [resp[17], 'Assist level 3 speed limit percentage']
    basic_dict['ALSL4'] = [resp[18], 'Assist level 4 speed limit percentage']
    basic_dict['ALSL5'] = [resp[19], 'Assist level 5 speed limit percentage']
    basic_dict['ALSL6'] = [resp[20], 'Assist level 6 speed limit percentage']
    basic_dict['ALSL7'] = [resp[21], 'Assist level 7 speed limit percentage']
    basic_dict['ALSL8'] = [resp[22], 'Assist level 8 speed limit percentage']
    basic_dict['ALSL9'] = [resp[23], 'Assist level 9 speed limit percentage']

    basic_dict['WD'] = [resp[24], 'Wheel diameter in inches / 2 - ({0} inches)'.format(resp[24]/2)]
    basic_dict['SM'] = [1, 'Speed meter type, and signals, BBS kits type is 0 or EXTERNAL']
    return basic_dict    

#-----------------------------------------------------------------------
# Get PAS config (b'\x11\x53')
#-----------------------------------------------------------------------
# Controller responds with 14 bytes
# Byte[0]     - Command [\x53]
# Byte[1]     - Response length
# Byte[2]     - PT,         Pedal Sensor Type, 0x00=None, 0x01=DH-Sensor-12, 0x02=BB-Sensor-32, 0x03=DoubleSignal-24
# Byte[3]     - DA,         Designated Assit Level, 0 to 9 or 0xff=by_display
# Byte[4]     - SL,         Speed Limit, 17 - 40 (in km/h) or 0xff=by_display
# Byte[5]     - SC,         Start Current
# Byte[6]     - SSM,        Slow Start Mode, (1..8)
# Byte[7]     - SDN,        Start degree
# Byte[8]     - WM,         Work Mode, 10 (Angular Speed of Pedal / Wheel * 10)
# Byte[9]     - SD,         Stop Delay, Time in 10's of milliseconds
# Byte[10]    - CD,         Current Decay, (1..8)
# Byte[11]    - TS,         Time of Stop, Time in 10's of milliseconds
# Byte[12]    - KC,         Keep Current, in %
# Byte[13]    - Checksum - no one cares
def get_pas_config():
    if test_data:
        resp = b'\x53\x0b\x03\xff\xff\x32\x04\x04\xff\x19\x08\x00\x3c\xec'
    else:
        resp = read_config(PAS_CMD)
    pas_dict['PT'] = [resp[2], 'Pedal sensor type, set by manufacturer, don\'t change']
    pas_dict['DA'] = [resp[3], 'Designated assist level - by display or 0-9']
    pas_dict['SL'] = [resp[4], 'Maximum speed limit which motor will assist to']
    pas_dict['SC'] = [resp[5], 'Start current % when rotating the pedals, recommend 10%']
    pas_dict['SSM'] = [resp[6], 'Slow start mode, how quickly start current is reached, recommend 4']
    pas_dict['SDN'] = [resp[7], 'Start degree, how many pedal pulses needed to start motor, recommed 4']
    pas_dict['WM'] = [resp[8], 'Work mode, angular pedal speed * 10, leave as set by manufacturer']
    pas_dict['SD'] = [resp[9], 'Stop delay * 10ms, delay after pedalling stops for motor to stop']
    pas_dict['CD'] = [resp[10], 'Current decay 1-8, how fast the current drops when pedaling faster']
    pas_dict['TS'] = [resp[11], 'Stop delay * 10ms, Time it takes for motor to stop']
    pas_dict['KC'] = [resp[12], 'Keep current %, Max current flowing at assist level, when pedaling']
    return pas_dict

#-----------------------------------------------------------------------
# Get THROTTLE config (b'\x11\x54')
#-----------------------------------------------------------------------
# Controller responds with 9 bytes
# Byte[0]     - Command [\x54]
# Byte[1]     - Response length
# Byte[2]     - Start Voltage * 100mV
# Byte[3]     - End Voltage * 100mV
# Byte[4]     - Mode - {SPEED = 0x00,  CURRENT = 0x01}
# Byte[5]     - Designated Assist Level
# Byte[6]     - Speed Limited km/h
# Byte[7]     - Start Current %
# Byte[8]     - Checksum
def get_throttle_config():
    if test_data:
        resp = b'\x54\x06\x0b\x24\x01\xff\x28\x0a\xb7'
    else:
        resp = read_config(THROTTLE_CMD)    
    throttle_dict['SV'] = [resp[2], 'Start voltage * 100mV, Throttle handle voltage when motor starts']
    throttle_dict['EV'] = [resp[3], 'End voltage * 100mV, Throttle handle voltage when motor is at max power']
    throttle_dict['MODE'] = [resp[4], "Mode of throttle handle, 0=\"speed\", 1=\"current\""]
    throttle_dict['DA'] = [resp[5], 'Designated assist level for throttle 0-9 or Display']
    throttle_dict['SL'] = [resp[6], 'Maximum speed level of throttle']
    throttle_dict['SC'] = [resp[7], 'Start current % for minimum throttle']
    return throttle_dict
    
#-----------------------------------------------------------------------
# Set BASIC config (b'\x16\x52' + data + checksum)
#-----------------------------------------------------------------------
def set_basic_config():
    frame = bytearray()
    frame.append(0x16)  # write command
    frame.append(0x52)  # section
    frame.append(0x18)  # packet length (24)
    c = 0x52 + 0x18
    for key in basic_dict:
        frame.append(basic_dict[key][0])
        c = c + basic_dict[key][0]
    checksum = c % 256
    print("Writing BASIC configs to controller...")
    frame.append(checksum)
    print("Sending -> {0}".format(hexlify(frame,',',1)))
    resp = read_config(frame)
    print("Response -> {0}".format(hexlify(resp,',',1)))
    if resp[1] != 0x18:
        print("Received error code {0} when writing to BASIC config".format(resp[2]))
        print("Error codes are:")
        print("  0) Low Battery Protection out of range")
        print("  1) Current Limit out of range")
        print("  2) Current Limit for PAS0 out of range")
        print("  3) Speed Limit for PAS0 out of range")
        print("  4) Current Limit for PAS1 out of range")
        print("  5) Speed Limit for PAS1 out of range")
        print("  6) Current Limit for PAS2 out of range")
        print("  7) Speed Limit for PAS2 out of range")
        print("  8) Current Limit for PAS3 out of range")
        print("  9) Speed Limit for PAS3 out of range")
        print("  10) Current Limit for PAS4 out of range")
        print("  11) Speed Limit for PAS4 out of range")
        print("  12) Current Limit for PAS5 out of range")
        print("  13) Speed Limit for PAS5 out of range")
        print("  14) Current Limit for PAS6 out of range")
        print("  15) Speed Limit for PAS6 out of range")
        print("  16) Current Limit for PAS7 out of range")
        print("  17) Speed Limit for PAS7 out of range")
        print("  18) Current Limit for PAS8 out of range")
        print("  19) Speed Limit for PAS8 out of range")
        print("  20) Current Limit for PAS9 out of range")
        print("  21) Speed Limit for PAS9 out of range")
        print("  22) Wheel Diameter out of range")
        print("  23) Speed Meter Signals out of range")
    else:
        print("Successfully written to BASIC controller config area...")

#-----------------------------------------------------------------------
# Set PAS config (b'\x16\x53' + data + checksum)
#-----------------------------------------------------------------------
def set_pas_config():
    frame = bytearray()
    frame.append(0x16)  # write command
    frame.append(0x53)  # section
    frame.append(0x0b)  # packet length (11)
    c = 0x53 + 0x0b
    for key in pas_dict:
        frame.append(pas_dict[key][0])
        c = c + pas_dict[key][0]
    checksum = c % 256
    print("Writing PAS configs to controller...")
    frame.append(checksum)
    print("Sending -> {0}".format(hexlify(frame,',',1)))
    resp = read_config(frame)
    print("Response -> {0}".format(hexlify(resp,',',1)))
    if resp[1] != 0x0b:
        print("Received error code {0} when writing to PAS config".format(resp[2]))
        print("Error codes are:")
        print("  0) Pedal Sensor Type error")
        print("  1) Designated Assist Level error")
        print("  2) Speed Limit error")
        print("  3) Start Current out of range")
        print("  4) Slow-start Mode error")
        print("  5) Start Degree out of range")
        print("  6) Work Mode error")
        print("  7) Stop Delay out of range")
        print("  8) Current Decay out of range")
        print("  9) Stop Decay out of range")
        print("  10) Keep Current out of range")
    else:
        print("Successfully written to PAS controller config area...")

#-----------------------------------------------------------------------
# Set THROTTLE config (b'\x16\x54' + data + checksum)
#-----------------------------------------------------------------------
def set_throttle_config():
    frame = bytearray()
    frame.append(0x16)  # write command
    frame.append(0x54)  # section
    frame.append(0x06)  # packet length
    c = 0x54 + 0x06
    for key in throttle_dict:
        frame.append(throttle_dict[key][0])
        c = c + throttle_dict[key][0]
    checksum = c % 256
    frame.append(checksum)
    print("Writing THROTTLE configs to controller...")
    print("Sending -> {0}".format(hexlify(frame,',',1)))
    resp = read_config(frame)
    print("Response -> {0}".format(hexlify(resp,',',1)))
    if resp[1] != 0x06:
        print("Received error code {0} when writing to THROTTLE config".format(resp[2]))
        print("Error codes are:")
        print("  0) Start voltage out of range")
        print("  1) End voltage out of range")
        print("  2) Mode error")
        print("  3) Designated Assist error")
        print("  4) Speed limit error")
        print("  5) Start current out of range ")
    else:
        print("Successfully written to THROTTLE controller config are...")
    #b'\x54\x06\x0b\x24\x01\xff\x28\x0a\xbb'

#-----------------------------------------------------------------------
# Get SPEED command (b'\x11\x20')
#-----------------------------------------------------------------------
# Controller returns 3 bytes
# The first byte is 0 when wheel RPM <= 256 and 1 or more when wheel 
# RPM > 256. 
# When wheel RPM > 256, the second byte starts from 0 again.
# The second byte (converted to decimal) holds the wheel RPM measured. 
# The third byte is a checksum (2nd byte + 20). 

# From these values, the speed (in km/h) of the bike can be calculated:
# rpm * wheelsize_in_meters * 60 / 1000
# ([byte 2] + ([byte 1]*256)) * wheelsize_in_meters * 60 / 1000)
#
# Example: a 28" inch wheel is 711mm
# Returned bytes: 0x00 0x3e 0x5e, 0x3e is 62.
# 62 + (0*256) = 62
# 62 *.711 * 60 / 1000 = 2.64 km/h
#
# The interval at which this message is sent is irregular 
# (ranging from .8 to a couple of seconds). So if you want to use speed 
# to determine distance traveled, you will need to know the time between 
# the two samples.
def get_speed():
    ser.write(SPEED_CMD)
    ser.flush()
    resp = ser.read(100)
    #print(hexlify(resp,',',1))
    wd_in_meters = basic_dict['WD'] * 25.4 / 1000
    print("Speed is {0}km/h".format((resp[1] + (resp[0]*256)) * wd_in_meters * 60 / 1000))

#-----------------------------------------------------------------------
# Get STATUS command (b'\x11\x08')
#-----------------------------------------------------------------------
# Controller returns 1 byte
# Values: 0 = Normal, 1 = Braking, 2 = Speed sensor error
def get_status():
    ser.write(STATUS_CMD)
    ser.flush()
    resp = ser.read(100)
    #print(hexlify(resp,',',1))
    if resp[0] == 1:
        print("Status -> Normal...")
    elif resp[0] == 3:
        print("Status -> Braking...")
    elif resp[0] == 21:
        print("Status -> Brake sensor error...")

#-----------------------------------------------------------------------
# Get BATTERY command (b'\x11\x11')
#-----------------------------------------------------------------------
# Controller returns 2 bytes
# The first and second bytes are identical.
# Value: battery percentage 0 - 100
def get_battery():
    ser.write(BATTERY_CMD)
    ser.flush()
    resp = ser.read(100)
    #print(hexlify(resp,',',1))
    print("Battery percentage -> {0}%...".format(resp[0]))

#-----------------------------------------------------------------------
# Get POWER command (b'\x11\x0a')
#-----------------------------------------------------------------------
# Controller returns 2 bytes
# The first and second bytes are identical.
# This byte is divided by two and holds the Amp value. 
# This value is the amount of amps the controller determined the motor
# should have, it is not a measured value. 
def get_power():
    ser.write(POWER_CMD)
    ser.flush()
    resp = ser.read(100)
    #print(hexlify(resp,',',1))
    print("POWER in Amps -> {0}A...".format(resp[0]/2))

#-----------------------------------------------------------------------
# Read a .bdac' config file into dictionaries and program flash
#-----------------------------------------------------------------------
def read_config_file(filename):
    global basic_dict, pas_dict, throttle_dict
    try:
        f = open(filename, 'r')
    except:
        print("Could not open {0}, exiting...".format(filename))
        sys.exit(0)
    # build one dictionary to hold the other 3
    fd = OrderedDict()
    # read it from the json file
    fd = json.load(f)

    # add them
    basic_dict =  fd['basic']
    pas_dict = fd['pas']
    throttle_dict = fd['throttle']

    print('{0} file successfully read...'.format(filename))

#-----------------------------------------------------------------------
# Write a .bdac config file (json format)
#-----------------------------------------------------------------------
def write_config_file(filename):
    try:
        f = open(filename, 'w')
    except:
        print('Could not open {0} for writing...'.format(filename))
        sys.exit(0)
    # build one dictionary to hold the other 3
    fd = OrderedDict()
    # add them
    fd['basic'] = basic_dict
    fd['pas'] = pas_dict
    fd['throttle'] = throttle_dict
    #write them to a json file
    json.dump(fd, f)
    f.close()

#-----------------------------------------------------------------------
# Read all configuration data from controller
#-----------------------------------------------------------------------
def read_flash():
    if test_data:
        print('\nAttention! Using TEST DATA, see help (bdac.py --help)...\n')
    get_info_config()
    get_basic_config()
    get_pas_config()
    get_throttle_config()

#-----------------------------------------------------------------------
# Write all configuration data to controller
#-----------------------------------------------------------------------
def write_flash():
    set_basic_config()
    set_pas_config()
    set_throttle_config()

#-----------------------------------------------------------------------
# Print all configuration data from controller
#-----------------------------------------------------------------------
def print_report(file=None):
    if file != None:
        read_config_file(file)

    print("Current Bafang controller flash settings with explainations.\n")

    print('[Basic]')
    for key in basic_dict:
        print("{0}\t{1}\t{2}".format(key, basic_dict[key][0],basic_dict[key][1]))
    
    print('\n', end = ""),
    print('[Pedal Assist]')
    for key in pas_dict:
        print("{0}\t{1}\t{2}".format(key, pas_dict[key][0],pas_dict[key][1]))
    
    print('\n', end = "")
    print('[Throttle Handle]')
    for key in throttle_dict:
        print("{0}\t{1}\t{2}".format(key, throttle_dict[key][0],throttle_dict[key][1]))

#=======================================================================
# Main
#=======================================================================
if __name__ == '__main__':
    test_data = False   # set to true to use test resp data
    help_text = """
 Usage:

    bdac                     Normal use, must have serial connection established.
    bdac --help              Print this help.
    bdac --test              Run bdac with test data.
    bdac --report            Retrieve controller settings and print report.
    bdac --report <filename> Retrieve settings from file and report.

 """

    if len(sys.argv) == 2 and str(sys.argv[1]) == "--help":
        print(help_text)
        sys.exit(0)
    elif len(sys.argv) == 2 and str(sys.argv[1]) == "--test":
        print("Using test data...")
        test_data = True   # set to true to use test resp data
    elif len(sys.argv) == 3 and str(sys.argv[1]) == "--report":
        print_report(file = str(sys.argv[2]))
        sys.exit()
    
    try:
        ser = Serial(PORT, 1200, timeout=1)
    except:
        print('Could not open serial port, using test data...')
        if test_data == False:
            print(help_text)
            #print('Exiting...')
            #sys.exit(0)
            test_data = True
            sys.argv = ['bdac.py', '--test']
    if len(sys.argv) == 1 or (len(sys.argv) >= 2 and str(sys.argv[1]) == "--test"):
        term = BdacTerm(get_basic_config, 
                        get_pas_config,
                        get_throttle_config,
                        read_config,
                        basic_dict,
                        pas_dict,
                        throttle_dict,
                        test_data,
                        PORT,
                        VERSION,
                        VERSION_DATE)
        curses.wrapper(term.gui_main, term)
    elif len(sys.argv) == 2 and str(sys.argv[1]) == "--report":
        read_flash()
        print_report()

    try:
        ser.close()
    except:
        pass
    sys.exit(0)

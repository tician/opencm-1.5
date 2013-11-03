#! /usr/bin/env python3

'''
 *******************************************************************************
 *  LEGAL STUFF
 *******************************************************************************
 *  Copyright (c) 2013 Matthew Paulishen. All rights reserved.
 *  
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *  
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *  
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *  
 *******************************************************************************
'''

import serial
import re
from optparse import OptionParser
import time

#python '{path}/{cmd}' --port={serial.port.file} -b '{build.path}/{build.project_name}.bin'

parser = OptionParser()
parser.add_option(  '-b', '--binary', dest='binFile',
                    help='Name of binary input file.',
                    metavar='FILE', action='store', type='string')
parser.add_option(  '-p', '--port', dest='port',
                    help='Serial port name/path.',
                    metavar='string', action='store', type='string')
parser.add_option(  '-s', '--size', dest='size',
                    help='Maximum permissible size of upload.',
                    metavar='int', action='store', type='int')

(options, args) = parser.parse_args()

fileName = options.binFile
if (not fileName):
	print ('You must provide an input file name.\n')
	exit()
	
portName = options.port
if (not portName):
	print ('You must provide a serial port to upload.\n')
	exit()

#if (re.match('COM', portName) != None):
#    print ('Using ' + portName + 'on Windows')
#elif (re.match('/dev/tty', portName) != None):
#    print ('Using ' + portName + 'on GNU/Linux')

#exit()

maxSize = 0
maxSize = options.size
if (maxSize == 0):
	print ('You must provide a maximum upload size.\n')
	exit()

buffBinary = []
buffChecksum = 0
buffSize = 0

# read binary file into 2k length buffers
binFile = open(fileName, 'r+b')
#TODO: add check for success

print ('Start loading file...')

while (True):
    tempbytes = binFile.read(256)
    if ( tempbytes != '' ):
        buffBinary.append(bytearray(tempbytes))
    else:
        break

binFile.close()
print ('done.')

for indexa in range(len(buffBinary)):
    for indexb in range(len(buffBinary[indexa])):
        buffChecksum += buffBinary[indexa][indexb]
        buffSize += 1

buffChecksum = buffChecksum & 0xFF
print ('File checksum = ' + hex(buffChecksum))

if (buffSize > maxSize):
    print ('Size of binary is larger than board limit')
    print (str(buffSize) + ' > ' + str(maxSize))
    exit()

chatter = serial.Serial()
chatter.baudrate = 115200
chatter.port = portName
chatter.timeout = 0.005
chatter.open()
#TODO: add check for success?


#if not open
#    print( 'Unable to open \'' + portName + '\'.  Check cable and/or try resetting the board.')
#    time.sleep(1)
    # retry some number of times
#    chatter.open()




'''
If sketch running, toggle DTR and send 'CM9X' to reboot to bootloader's SerialMonitor()

Upon reset, CM9 bootloader will send a byte of data to identify itself as a CDC device (0x0A - CDC_DATA)?

Within SerialMonitor() of the bootloader:
Sending 'AT' to the bootloader causes it to respond with 'OK'. (does not appear to work on pre-CM-904)

Sending 'AT&RST' to the bootloader causes a board reset. (not sure if works on pre-CM-904)

Sending 'AT&TOSS' to the bootloader causes the CM9 to enter dynamixel toss mode (pass-through). (does not appear to work on pre-CM-904)

Sending 'AT&NAME' to the bootloader responds with the board name (CM-904). (does not appear to work on pre-CM-904)

Sending 'AT&GO' starts the user application.

Sending 'AT&LD' to the bootloader causes it to erase the user flash memory.  Once that is done, the CM9 responds with 'Ready..'.  The PC then starts sending the binary file in chunks up to 2048 bytes in length until the file is completely sent.  After that the PC sends the single byte checksum which is the sum of all bytes in the binary file.  The CM9 responds with either 'Success..' or 'Failure..', at which point you either send 'AT&GO' to start the firmware or resend 'AT&LD' to retry the download.
'''

'''
	PC sends 'AT&LD'
	CM9 sends 'Ready..'
	PC sends binary data in chunks up to 2048 in length.
	Unnecessary?: PC sets DTR true
	PC sends checksum byte
		Checksum is single byte sum of every byte sent in binary file.
	CM9 sends 'Success..' or 'Fail..'
	if 'Success..'
		print ('Download succeeded. Starting sketch...\n')
		PC sends AT&GO
		exit()
	else
		print ('Download failed. Retrying...\n')
'''

#debug
#chatter.write('AT&GO')
#time.sleep(5)

# Check if already in bootloader SerialMonitor()

'''
# only works for CM-904 bootloader and later
while True:
    time.sleep(1)
    chatter.write('AT')
#    chatter.write('AT&LD')
    time.sleep(1)
    resp = chatter.read(2)
    print(resp)
    chatter.flushInput()

    if (re.match('OK',resp) != None):
        print ('In bootloader and ready for upload')

        chatter.write('AT&LD')
        eraserTimeout = 0
        readr = chatter.read(20)
        while (readr == '' and eraserTimeout < 200):
            readr = chatter.read(20)
            eraserTimeout += 1

        if (re.match('Ready..',readr) != None):
            print ('Downloading...')
            for indexa in range(len(buffBinary)):
                chatter.write(buffBinary[indexa])
            chatter.setDTR(True)
            chatter.write(chr(buffChecksum))

            stat = chatter.read(20)
            while (stat == ''):
                stat = chatter.read(20)
            chatter.flushInput()

            if (re.match('Success..',stat) != None ):
                print ('succeeded.')
                time.sleep(3)
                chatter.write('AT&GO')
                break
            else:
                print ('failed.')
        else:
            print ('Did not receive expected response from bootloader')
            print ('Received: ' + readr)

    else:
    # Not in bootloader, trigger an IWDG timeout reset
       print ('Not in bootloader mode. Triggering reset.\n')
        chatter.setDTR(False)
        time.sleep(.5)
        chatter.setDTR(True)
        time.sleep(.5)
        chatter.write('CM9X')
        chatter.close()
        time.sleep(5)
        chatter.open()
'''

while True:
    rebootToBootloader = 0

    time.sleep(1)
    chatter.flushInput()
    chatter.write('AT&LD')
    time.sleep(1)
    resp = chatter.read(20)
    while (resp == '' and rebootToBootloader < 200):
        resp = chatter.read(20)
        rebootToBootloader += 1
#    print(resp)
    chatter.flushInput()

    if ( re.match('Ready..', resp) != None ):
#        print ('In bootloader and ready for upload.')
#        time.sleep(0.05)

        print ('Downloading...')
        for indexa in range(len(buffBinary)):
            chatter.write(buffBinary[indexa])
#            time.sleep(0.05)
        chatter.setDTR(True)
        chatter.write(chr(buffChecksum))

        stat = chatter.read(20)
        while (stat == ''):
            stat = chatter.read(20)
#        print(stat)
        chatter.flushInput()
#        if (re.match('Fail', stat) != None ):
#            print ('failed.')
#            continue
        if (re.match('Success..',stat) != None ):
            print ('succeeded.')
            time.sleep(3)
            chatter.write('AT&GO')
            break
        else:
            print ('failed.')

    else:
    # Not in bootloader, trigger an IWDG timeout reset
        print ('Not in bootloader mode. Triggering reset.')
#        chatter.setDTR(True)
#        time.sleep(.5)
        chatter.setDTR(False)
        time.sleep(.5)
        chatter.setDTR(True)
        time.sleep(.5)
        chatter.write('CM9X')
        chatter.close()
        time.sleep(5)
        chatter.open()


exit()


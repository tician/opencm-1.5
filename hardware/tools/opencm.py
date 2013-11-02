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


#python '{path}/{cmd}' --port={serial.port.file} -b '{build.path}/{build.project_name}.bin'

parser = OptionParser()
parser.add_option(  '-b', '--binary', dest='binFile',
                    help='Name of binary input file.',
                    metavar='FILE', action='store', type='string')
parser.add_option(  '-p', '--port', dest='port',
                    help='Serial port name/path.',
                    metavar='string', action='store', type='string')

(options, args) = parser.parse_args()

fileName = options.binFile
if (not fileName):
	print ('You must provide an input file name.\n')
	exit()

portName = options.port
if (not portName):
	print ('You must provide a serial port to upload.\n')
	exit()



strDownloadReady = 'Ready..'
strDownloadSuccess = 'Success..'
strDownloadFail = 'Fail..'


buffBinary = []
#buffChecksum = bytearray(1)
buffChecksum = 0

# read binary file into 2k length buffers
binFile = open(fileName, 'r+b')
while (True):
    tempbytes = binFile.read(2048)
    if ( tempbytes != '' ):
#        buffBinary.append(tempbytes)
        buffBinary.append(bytearray(tempbytes))
    else:
        break

binFile.close()

for indexa in range(len(buffBinary)):
    for indexb in range(len(buffBinary[indexa])):
#        buffChecksum[0] += buffBinary[indexa][indexb]
        buffChecksum += buffBinary[indexa][indexb]

#        buffChecksum[0] += int.from_bytes(buffBinary[indexa][indexb])
#        buffChecksum += int.from_bytes(buffBinary[indexa][indexb])
 
#        tempest = int(buffBinary[indexa][indexb])
#        buffChecksum[0] += tempest

#print(hex(buffChecksum[0]))

buffChecksum = buffChecksum & 0xFF
print (hex(buffChecksum))
exit()




chatter = serial.Serial()
chatter.baudrate = 115200
chatter.port = portName
chatter.timeout = 0.5
chatter.open()



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

'''

# Check if already in bootloader SerialMonitor()
chatter.send('AT&LD')
resp = chatter.read()

if (re.match(resp,strDownloadReady) == None):
# Not in bootloader, trigger an IWDG timeout reset


elif (re.match(resp,strDownloadReady) != None):
    for index in range(len(buffBinary)):
        chatter.send(buffBinary[index])



'''

exit()

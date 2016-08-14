#!/usr/bin/env python

import fingerpi as fp

import time
# from fingerpi.fingerpi_base import command

# from fingerpi.fingerpi_base import checksum as cs
# from fingerpi.fingerpi_base import make_bytearray as mb
# from fingerpi.fingerpi_base import printBytearray

f = fp.FingerPi('/dev/ttyAMA0', baudrate = 9600)

print f.Open(extra_info = True, check_baudrate = True)
print f.ChangeBaudrate(57600)


print f.sendCommand(command('CmosLed'), 0)
time.sleep(1)
print f.sendCommand(command('CmosLed'), 1)
time.sleep(1)

print f.GetEnrollCount()

print f.ChangeBaudrate(57600)

for idx in xrange(10):
    print f.sendCommand(command('CmosLed'), 0)
    time.sleep(1)
    print f.sendCommand(command('CmosLed'), 1)
    time.sleep(1)

print f.sendCommand(command('CmosLed'), 0)


print f.sendCommand(command('Close'))



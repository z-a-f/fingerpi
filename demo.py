#!/usr/bin/env python

import fingerpi as fp
from fingerpi.base import make_packet
import time
import serial
# from fingerpi.fingerpi_base import command

# from fingerpi.fingerpi_base import checksum as cs
# from fingerpi.fingerpi_base import make_bytearray as mb
# from fingerpi.fingerpi_base import printBytearray

def byte2list(arr):
    assert type(arr) == bytearray
    res = []
    for el in arr:
        res.append(hex(el))
    return res

print byte2list(make_packet('comm', command = 'Open'))

ser = serial.Serial(port = '/dev/cu.usbmodem1421', timeout = 2., baudrate = 9600)

packet = make_packet('comm', command = 'CmosLed', parameter = 1)
print ser.write(packet)
print ser.read(12)




#!/usr/bin/env python

import fingerpi as fp
from fingerpi import base

import struct, time

def printByteArray(arr):
    return map(hex, list(arr))

f = fp.FingerPi()

print f.Open(extra_info = True, check_baudrate = True)
print f.ChangeBaudrate(57600)
print f.CheckEnrolled(300)
print f.GetEnrollCount()
print f.CmosLed(True)
time.sleep(1)
print f.CmosLed(False)
print f.Close()

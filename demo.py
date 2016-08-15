#!/usr/bin/env python

import fingerpi as fp
from fingerpi import base

import struct

def printByteArray(arr):
    return map(hex, list(arr))

f = fp.FingerPi()

print f.Open(check_baudrate = True)

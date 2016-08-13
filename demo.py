#!/usr/bin/env python

import fingerpi as fp

from fingerpi.fingerpi_base import command

from fingerpi.fingerpi_base import checksum as cs
from fingerpi.fingerpi_base import make_bytearray as mb
from fingerpi.fingerpi_base import printBytearray

f = fp.FingerPi(port = None)
f.sendCommand(command('Open'), 0)



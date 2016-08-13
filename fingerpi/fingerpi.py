
"""Communication with the Fingerprint Scanner using R-Pi1"""

import os, sys
import serial

from .base import (_fp_command, _fp_response,  _fp_error)

class FingerPi(serial.Serial):
    def __init(self, port = '/dev/ttyAMA0', baudrate = 9600, *args, **kwargs):
        ## First check if serial port is openable :)
        if not os.pathexixsts(port):
            raise IOError("Port " + port + " cannot be opened!")
        super(FingerPi, self).__init__(port = port, baudrate = baudrate, *args, **kwargs)

    
        

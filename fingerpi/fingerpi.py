
"""Communication with the Fingerprint Scanner using R-Pi1"""

import os, sys
import serial

from .base import * # (_fp_command, _fp_response,  _fp_error)

class FingerPi(serial.Serial):
    def __init__(self, port = '/dev/ttyAMA0', baudrate = 9600, device_id = 0x01, *args, **kwargs):
        ## First check if serial port is openable :)
        if not os.path.exists(port):
            raise IOError("Port " + port + " cannot be opened!")
        super(FingerPi, self).__init__(port = port, baudrate = baudrate, *args, **kwargs)

        self._command_start_code_1 = 0x55
        self._command_start_code_1 = 0xAA
        self._device_id = device_id
        
    def _make_packet(self, command, parameter = None):
        if type(command) == str:
            command = _fp_command(command)
        if parameter is None:
            parameter = 0

        command = _make_bytearray(command, _WORD, '<', True)
        parameter = _make_bytearray(parameter, _DWORD, '<', True)



        
        

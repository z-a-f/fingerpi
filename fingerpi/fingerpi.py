
"""Communication with the Fingerprint Scanner using R-Pi"""

import os, sys
import serial

# from .base import * # (_fp_command, _fp_response,  _fp_error)
import fingerpi_base

from fingerpi_base import printBytearray

class FingerPi():
    def __init__(self,
                 port = '/dev/ttyAMA0',
                 baudrate = 9600,
                 device_id = 0x01,
                 *args, **kwargs
    ):
        ## First check if serial port is openable :)
        if not os.path.exists(port):
            raise IOError("Port " + port + " cannot be opened!")
        # super(FingerPi, self).__init__(
        #     port = port, baudrate = baudrate, *args, **kwargs)
        self.serial = serial.Serial(
            port = port, baudrate = baudrate, *args, **kwargs)
        
        self._device_id = fingerpi_base.make_bytearray(
            device_id, fingerpi_base.WORD, '<', True)

    def sendCommand(self, command, parameters, verbosity = 0):
        packet = self._make_packet(command, parameters)
        print self.serial.write(packet)
        # self.serial.flush()
        print list(packet)
        print list(self.serial.read(12))
        
    def _make_packet(self, command, parameter = None, start_code = None):
        """
        Note that if the command is specified adirectly as an INT, it will
        not be checked!!!
        """
        if type(command) == str:
            command = fingerpi_base.command(command)
        if parameter is None:
            parameter = 0

        if start_code is None:
            start_code = fingerpi_base.start_codes('Command')
        
        start_code = fingerpi_base.make_bytearray(
            start_code, fingerpi_base.WORD, '>', False)
        command = fingerpi_base.make_bytearray(
            command, fingerpi_base.WORD, '<', True)
        parameter = fingerpi_base.make_bytearray(
            parameter, fingerpi_base.DWORD, '<', True)

        res = start_code + self._device_id + command + parameter
        # print sum(res)
        res += fingerpi_base.checksum(res)

        return res
    
    

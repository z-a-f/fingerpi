
"""Communication with the Fingerprint Scanner using R-Pi"""

import os, sys
import serial

from .base import *
# from .base import * # (_fp_command, _fp_response,  _fp_error)
# import fingerpi_base

# from fingerpi_base import printBytearray

class FingerPi():
    
    
    def __init__(self,
                 port = '/dev/ttyAMA0',
                 baudrate = 9600,
                 device_id = 0x01,
                 *args, **kwargs
    ):
        ## First check if serial port is openable :)
        # super(FingerPi, self).__init__(
        #     port = port, baudrate = baudrate, *args, **kwargs)
        if port is None:
            port = '/dev/ttyAMA0'
        self.port = port
        self.baudrate = baudrate
        if not os.path.exists(port):
            raise IOError("Port " + self.port + " cannot be opened!")

        self.serial = serial.Serial(
            port = self.port, baudrate = self.baudrate, *args, **kwargs)

        self.device_id = device_id

    
    ##########################################################
    ## Individual command implementation

    ## Base:
    def sendCommand(self, command, parameter = 0x00, data = None, data_len = 0, data_in_len = 0):
        if command == 'data':
            packet = make_packet('data', device_id = self.device_id, data = data, data_len = data_len)
        else:
            packet = make_packet('comm', device_id = self.device_id, parameter = parameter, command = command)

        while not self.serial.writable():
            pass
        command_res = self.serial.write(packet)
        response = self.serial.read(12)

        if command == 'data':
            response = decode_packet('data', packet = response, data_len = data_len)
        else:
            response = decode_packet('comm', packet = response)

        if data_in_len > 0:
            response['Data'] = self.serial.read(data_in_len)

        response = response

        return response

    def Open(self, extra_info = False, check_baudrate = False):
        # Check baudrate:
        if check_baudrate:
            self.serial.timeout = 0.5
            for baudrate in [self.serial.baudrate] + self.serial.BAUDRATES:
                if 9600 <= baudrate <= 115200:
                    self.serial.baudrate = baudrate
                    resp = self.sendCommand('Open')
                    print resp
                    if resp['Start Code'] is not None:
                        break
            if self.serial.baudrate > 115200:
                raise RuntimeError("Couldn't find appropriate baud rate!")
                
        if extra_info:
            return self.sendCommand('Open', 1)
        else:
            return self.sendCommand('Open')

    def Close (self):
        self.ChangeBaudrate(9600)
        return self.sendCommand('Close')

    def UsbInternalCheck(self):
        return self.sendCommand('UsbInternalCheck')

    def CmosLed(self, on = False):
        if on:
            return self.sendCommand('CmosLed', 1)
        else:
            return self.sendCommand('CmosLed', 0)

    def ChangeBaudrate(self, baudrate):
        resp = self.sendCommand('ChangeBaudrate', baudrate)
        self.serial.baudrate = baudrate
        return resp

    def GetEnrollCount(self):
        return self.sendCommand('GetEnrollCount')

    def CheckEnrolled(self, ID):
        return self.sendCommand('CheckEnrolled', ID)

    def EnrollStart(self, ID):
        return self.sendCommand('EnrollStart', ID)

    def Enroll1(self):
        return self.sendCommand('Enroll1')

    def Enroll2(self):
        return self.sendCommand('Enroll2')

    def Enroll3(self):
        return self.sendCommand('Enroll3', True, 498 + 6)

    def IsPressFinger(self):
        return self.sendCommand('IsPressFinger')

    def DeleteId(self, ID):
        return self.sendCommand('DeleteID', ID)

    def DeleteAll(self):
        return self.sendCommand('DeleteAll')

    def Verify(self, ID):
        return self.sendCommand('Verify', ID)

    def Identify(self):
        return self.sendCommand('Identify')


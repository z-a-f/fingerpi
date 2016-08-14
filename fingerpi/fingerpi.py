
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
    def sendCommand(self, command, parameter = 0x00, data = None, data_len = 0):
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

        return response

        # packet = self._make_packet(command, parameters)
        # while not self.serial.writable():
        #     pass
        # command_res = self.serial.write(packet)
        # resp = self.serial.read(12)
        # resp = self._response_decode(resp)
        
        # data = []

        # if data_packet:
        #     data = self.serial.read(data_len)
        #     data = self._response_decode(data, 'd')
        #     data = [data_len, data]
        
        # return [resp, data]

    def Open(self, extra_info = False, check_baudrate = False):
        # Check baudrate:
        if check_baudrate:
            self.serial.timeout = 0.5
            for baudrate in self.serial.BAUDRATES:
                if 9600 <= baudrate <= 115200:
                    self.serial.baudrate = baudrate
                    resp = self.sendCommand('Open')
                    # print resp
                    if resp[0] is not None:
                        break
            if self.serial.baudrate > 115200:
                raise RuntimeError("Couldn't find appropriate baud rate!")
                
        if extra_info:
            return self.sendCommand('Open', 0x01, True, 30)
        else:
            return self.sendCommand('Open')

    def Close (self):
        self.ChangeBaudrate(9600)
        return self.sendCommand('Close')

    def UsbInternalCheck(self):
        return self.sendCommand('UsbInternalCheck')

    def CmosLed(self, on = False):
        if on:
            return self.sendCommand('CmosLed', 0)
        else:
            return self.sendCommand('CmosLed', 1)

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

    
        
    
    ##
    #########################################################
    
    # def _make_packet(self, command, parameter = None, start_code = None):
    #     """
    #     Note that if the command is specified adirectly as an INT, it will
    #     not be checked!!!
    #     """
    #     if type(command) == str:
    #         command = fingerpi_base.command(command)
    #     if parameter is None:
    #         parameter = 0

    #     if start_code is None:
    #         start_code = fingerpi_base.start_codes('Command')
        
    #     start_code = fingerpi_base.make_bytearray(
    #         start_code, fingerpi_base.WORD, '>', False)
    #     command = fingerpi_base.make_bytearray(
    #         command, fingerpi_base.WORD, '<', True)
    #     parameter = fingerpi_base.make_bytearray(
    #         parameter, fingerpi_base.DWORD, '>', True)

    #     res = start_code + self._device_id + parameter + command
    #     # print sum(res)
    #     res += fingerpi_base.checksum(res)
    #     # print list(parameter)
    #     return res

    # def _response_decode(self, response, packet = 'r'):
    #     assert packet == 'r' or packet == 'd'
    #     res = []
    #     if response == '':
    #         return None
    #     if packet == 'r':
    #         # print "ACK: ", map(ord,list(response[8:10]))
    #         res.append(fingerpi_base.start_codes(response[:2]))
    #         res.append(response[2:4])
    #         res.append(fingerpi_base.error(response[4:8]))
    #         res.append(fingerpi_base.response(response[8:10]))
    #         res.append(response[10:])
    #     else:
    #         ln = len(res)
    #         data_len = ln - 6
    #         res.append(fingerpi_base.start_codes(response[:2]))
    #         res.append(response[2:4])
    #         res.append(response[4:4+data_len])
    #         res.append(response[4+data_len:])

    #     return res
    


"""Communication with the Fingerprint Scanner using R-Pi"""

import os, sys
import serial

from .base import *

class FingerPi():
    def __init__(self,
                 port = '/dev/ttyAMA0',
                 baudrate = 9600,
                 device_id = 0x01,
                 timeout = 2,
                 *args, **kwargs):
        self.port = port
        self.baudrate = baudrate
        if not os.path.exists(port):
            raise IOError("Port " + self.port + " cannot be opened!")

        self.serial = serial.Serial(
            port = self.port, baudrate = self.baudrate, timeout = timeout,
            *args, **kwargs)

        self.device_id = device_id
        self.timeout = 5

        self.save = False

        self.serial.flushInput()
        self.serial.flushOutput()

    
    ##########################################################
    ## Send/Get routines

    def sendCommand(self, command, parameter = 0x00):
        if type(parameter) == bool:
            parameter = parameter*1
        packet = encode_command_packet(command, parameter, device_id = self.device_id)

        # The length of the written command should match:
        result = len(packet) == self.serial.write(packet)
        self.serial.flush()
        return result

    def getResponse(self, response_len = 12):
        response = self.serial.read(response_len)
        # print len(response)
        return decode_command_packet(bytearray(response))

    def sendData(self, data, data_len):
        packet = encode_data_packet(data, data_len, device_id = self.device_id)
        result = len(packet) == self.serial.write(packet)
        self.serial.flush()
        return result

    def getData(self, data_len):
        # Data length is different for every command
        response = self.serial.read(1+1+2+data_len+2) # Header(2) + ID(2) + data + checksum(2)
        # return response
        return decode_data_packet(bytearray(response))


    ##########################################################
    ## Send/Get routines
    def Open(self, extra_info = False, check_baudrate = False):
        # Check baudrate:
        if check_baudrate:
            self.serial.timeout = 0.5
            for baudrate in (self.serial.baudrate,) + self.serial.BAUDRATES:
                if 9600 <= baudrate <= 115200:
                    self.serial.baudrate = baudrate
                    if not self.sendCommand('Open', extra_info):
                        raise RuntimeError("Couldn't send 'Open' packet!")
                    # print baudrate
                    response = self.getResponse()
                    if response['ACK']:
                        # Decoded something
                        response['Parameter'] = baudrate
                        break
                    
            if self.serial.baudrate > 115200: # Cannot be more than that
                raise RuntimeError("Couldn't find appropriate baud rate!")
        else:
            self.sendCommand('Open', extra_info)
            response = self.getResponse()
        data = None
        if extra_info:
            data = self.getData(16+4+4)
        self.serial.timeout = self.timeout
        return [response, data]

    def Close (self):
        self.ChangeBaudrate(9600)
        if self.sendCommand('Close'):
            response = self.getResponse()
            self.serial.flushInput()
            self.serial.flushOutput()
            self.serial.close()
            return [response, None]
        
        else:
            raise RuntimeError("Couldn't send packet")

    def UsbInternalCheck(self):
        if self.sendCommand('UsbInternalCheck'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def CmosLed(self, on = False):
        if self.sendCommand('CmosLed', on):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def ChangeBaudrate(self, baudrate):
        if self.sendCommand('ChangeBaudrate', baudrate):
            response = self.getResponse()
            self.serial.baudrate = baudrate
            return [response, None]
        else:
            raise RuntimeError("Couldn't send packet")

    def GetEnrollCount(self):
        if self.sendCommand('GetEnrollCount'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def CheckEnrolled(self, ID):
        if self.sendCommand('CheckEnrolled', ID):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def EnrollStart(self, ID):
        self.save = ID == -1
        if self.sendCommand('EnrollStart', ID):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def Enroll1(self):
        if self.sendCommand('Enroll1'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def Enroll2(self):
        if self.sendCommand('Enroll2'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def Enroll3(self):
        if self.sendCommand('Enroll3'):
            response = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet")
        data = None
        if self.save:
            data = self.getData(498)
        return [response, data]

    def IsPressFinger(self):
        if self.sendCommand('IsPressFinger'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def DeleteId(self, ID):
        if self.sendCommand('DeleteId', ID):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def DeleteAll(self):
        if self.sendCommand('DeleteAll'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def Verify(self, ID):
        if self.sendCommand('Verify'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def Identify(self):
        if self.sendCommand('Identify'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def VerifyTemplate(self, ID, template):
        if self.sendCommand('VerifyTemplate', ID):
            response = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet")
        if self.sendData(template, 498):
            data = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet (data)")
        return [response, data]

    def IdentifyTemplate(self, template):
        if self.sendCommand('IdentifyTemplate'):
            response = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet")
        if self.sendData(template, 498):
            data = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet (data)")
        return [response, data]

    def CaptureFinger(self, best_image = False):
        # For enrollment use 'best_image = True'
        # For identification use 'best_image = False'
        if best_image:
            self.serial.timeout = 10
        if self.sendCommand('CaptureFinger', best_image):
            self.serial.timeout = self.timeout
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def MakeTemplate(self):
        if self.sendCommand('MakeTemplate'):
            response = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet")
        self.serial.timeout = 10
        data = self.getData(498)
        self.serial.timeout = self.timeout
        return [response, data]

    def GetImage(self, dim = (258, 202)):
        # The documentation is ambiguous:
        # Dimensions could be 202x258 or 256x256
        to_read = dim[0]*dim[1]

        if self.sendCommand('GetImage'):
            response = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet")
        data = None
        if response['ACK']:
            self.serial.timeout = None # This is dangerous!
            data = self.getData(dim[0]*dim[1])
            self.serial.timeout = self.timeout
            data['Data'] = (data['Data'], dim)
        return [response, data]

    def GetRawImage(self, dim = (160, 120)):
        if self.sendCommand('GetRawImage'):
            response = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet")
        data = None
        if response['ACK']:
            self.serial.timeout = None # This is dangerous!
            data = self.getData(dim[0]*dim[1])
            self.serial.timeout = self.timeout
            # Add dimensions to the data
            data['Data'] = (data['Data'], dim)
        return [response, data]

    def GetTemplate(self, ID):
        if self.sendCommand('GetTemplate', ID):
            response = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet")
        self.serial.timeout = None # This is dangerous!
        data = self.getData(498)
        self.serial.timeout = self.timeout
        return [response, data]

    def SetTemplate(self, ID, template):
        if self.sendCommand('SetTemplate', ID):
            response = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet")
        if self.sendData(template, 498):
            data = self.getResponse()
        else:
            raise RuntimeError("Couldn't send packet (data)")
        return [response, data]

    def GetDatabaseStart(self):
        if self.sendCommand('GetDatabaseStart'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def GetDatabaseEnd(self):
        if self.sendCommand('GetDatabaseEnd'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")

    def SetIAPMode(self):
        if self.sendCommand('SetIAPMode'):
            return [self.getResponse(), None]
        else:
            raise RuntimeError("Couldn't send packet")


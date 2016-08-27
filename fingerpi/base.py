
import struct
from .structure import *


"""
Command Packet:
OFFSET  ITEM        TYPE    DESCRIPTION
----------------------------------------------------------------
0       0x55        BYTE    Command start code 1
1       0xAA        BYTE    Command start code 2
2       Device ID   WORD    Device ID (default: 0x0001)
4       Parameter   DWORD   Input parameter
8       Command     WORD    Command code
10      Checksum    WORD    Byte addition checksum

Response Packet:
OFFSET  ITEM        TYPE    DESCRIPTION
----------------------------------------------------------------
0       0x55        BYTE    Response code 1
1       0xAA        BYTE    Response code 2
2       Device ID   WORD    Device ID (default: 0x0001)
4       Parameter   DWORD   Error code
8       Response    WORD    Response (ACK/NACK)
10      Checksum    WORD    Byte addition checksum

Data Packet:
OFFSET  ITEM        TYPE    DESCRIPTION
----------------------------------------------------------------
0       0x5A        BYTE    Data code 1
1       0xA5        BYTE    Data code 2
2       Device ID   WORD    Device ID (default: 0x0001)
4       Parameter   N BYTES N bytes of data - size predefined
4 + N   Checksum    WORD    Byte addition checksum
"""

"""
Args:
    typ: Type of the packet to create
        'comm': Command/Response packet
        'data': Data packet
    device_id: Device ID (defualts to 1)
    parameter: Parameter to send
    command: Command to send
"""

def encode_command_packet(
        command = None,
        parameter = 0,
        device_id = 1):
    
    command = commands[command]
    packet = bytearray(struct.pack(comm_struct(), 
        packets['Command1'],    # Start code 1
        packets['Command2'],    # Start code 2
        device_id,              # Device ID
        parameter,              # Parameter
        command                 # Command
    ))
    checksum = sum(packet)
    packet += bytearray(struct.pack(checksum_struct(), checksum))
    return packet

def encode_data_packet(
        data = None,
        data_len = 0,
        device_id = 1):
    
    packet = bytearray(struct.pack(data_struct(data_len), 
        packets['Data1'],    # Start code 1
        packets['Data2'],    # Start code 2
        device_id,           # Device ID
        data                 # Data to be sent
    ))
    checksum = sum(packet)
    packet += bytearray(struct.pack(checksum_struct(), checksum))
    return packet

def decode_command_packet(packet):
    response = {
        'Header': None,
        'DeviceID': None,
        'ACK': None,
        'Parameter': None,
        'Checksum': None        
    }
    _debug = packet
    if packet == '': # Nothing to decode
        response['ACK'] = False
        return response
    # Check if it is a data packet:
    if packet[0] == packets['Data1'] and packet[1] == packets['Data2']:
        return decode_data_packet(packet)
    # Strip the checksum and get the values out
    checksum = sum(struct.unpack(checksum_struct(), packet[-2:])) # Last two bytes are checksum
    packet = packet[:-2]
    response['Checksum'] = sum(packet) == checksum # True if checksum is correct

    try:
        packet = struct.unpack(comm_struct(), packet)
    except Exception as e:
        raise Exception(str(e) + ' ' + str(packet[0]))
    response['Header'] = hex(packet[0])[2:] + hex(packet[1])[2:]
    response['DeviceID'] = hex(packet[2])[2:]
    response['ACK'] = packet[4] != 0x31 # Not NACK, might be command
    # response['Parameter'] = packet[3] if response['ACK'] else errors[packet[3]]
    response['Parameter'] = errors(packet[3]) if (not response['ACK'] and packet[3] in errors) else packet[3]

    return response

def decode_data_packet(packet):
    response = {
        'Header': None,
        'DeviceID': None,
        'Data': None,
        'Checksum': None        
    }
    if packet == '':
        response['ACK'] = False
        return response
    # Check if it is a command packet:
    if packet[0] == packets['Command1'] and packet[1] == packets['Command2']:
        return decode_command_packet(packet)
    
    # Strip the checksum and get the values out
    checksum = sum(struct.unpack(checksum_struct(), packet[-2:])) # Last two bytes are checksum
    packet = packet[:-2]
    # Data sum might be larger than the checksum field:
    chk = sum(packet)
    chk &= 0xffff
    response['Checksum'] = chk == checksum # True if checksum is correct
    
    data_len = len(packet) - 4 # Exclude the header (2) and device ID (2)

    packet = struct.unpack(data_struct(data_len), packet)
    response['Header'] = hex(packet[0])[2:] + hex(packet[1])[2:]
    response['DeviceID'] = hex(packet[2])[2:]
    response['Data'] = packet[3]
    # print packet
    return response





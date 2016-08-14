
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
def make_packet(
        typ = 'comm', 
        device_id = 1,
        parameter = 0,
        command = None,
        data = None,
        data_len = 0):
    
    structure = ''
    command = commands[command]

    if typ == 'comm':
        structure = comm_struct()
        packet = bytearray(struct.pack(structure, 
            packets['Command1'],    # Start code 1
            packets['Command2'],    # Start code 2
            device_id,              # Device ID
            parameter,              # Parameter
            command                 # Command
        ))
    elif typ == 'data':
        structure = data_struct(data_len)
        packet = bytearray(struct.pack(structure,
            packets['Data1'],
            packets['Data2'],
            device_id,
            data
        ))
    else:
        raise InputError("Command type unknown")
    checksum = sum(packet)
    packet += bytearray(struct.pack(checksum_struct(), checksum))
    return packet

def decode_packet(typ = 'comm', packet = None, data_len = 0):
    res = {
        'Start Code': None,
        'Device ID': None,
        'Response': None,
        'Error Code': None,
        'Data': None,
        'Checksum': None
    }
    structure = ''
    if type(packet) != bytearray:
        packet = bytearray(packet)
    print len(packet)
    checksum = struct.unpack(checksum_struct(), packet[-2:])
    res['Checksum'] = sum(packet[:-2]) != checksum

    if typ == 'comm':
        packet = struct.unpack(comm_struct(), packet[:-2])
        # code = hex(packet[0])[2:] + hex(packet[1])[2:]
        # res['Start Code'] = packets[int(code, 16)]
        res['Start Code'] = packets[0x55AA]
        res['Device ID'] = packet[2]
        res['Response'] = packet[4]
        res['Error Code'] = errors[packet[3]] if (res['Response'] == 'Nack') else None
    elif typ == 'data':
        packet = struct.unpack(data_struct(data_len), packet[:-2])
        # code = hex(packet[0])[2:] + hex(packet[1])[2:]
        # res['Start Code'] = packets[int(code, 16)]
        res['Start Code'] = packets[0x5AA5]
        res['Device ID'] = packet[2]
        res['Data'] = packet[3:-2]
    else:
        raise InputError('Command type unknown')

    return res





BYTE = 1
WORD = 2
DWORD = 4

def printBytearray(ba):
    assert type(ba) == bytearray
    res = '[ '
    for el in ba:
        add = ''
        if el > 255:
            add = '0'
        el = hex(el)[2:]
        el = '0x'+add+el
        
        res += el + ' '
    return res + ']'
        
def checksum(arr):
    if type(arr) != bytearray:
        raise NotImplementedError("Cannot compute checksum of type " + type(arr))
    return make_bytearray(sum(arr), WORD, '<', True)
    
def make_bytearray(arr, length = 1, endian = '>', tail_padding = False):
    """
    Note:
    	If the input is a 'bytearray', it is returned as is!
    Args:
        endian:
    	    >: The order will be in the order the input is given
	    <: The order will be reversed
    	tail_padding:
    	    Apply padding in the end of the returned array.
    Examples:
    	>>> _make_bytearray([1, 2], 4, '<', True)
    	bytearray('\x02\x01\x00\x00')

    	>>> _make_bytearray([1, 2], 4, '>', True)
    	bytearray('\x01\x02\x00\x00')

    	>>> _make_bytearray([1, 2], 4, '<', False)
    	bytearray('\x00\x00\x02\x01')

    	>>> _make_bytearray([1, 2], 4, '>', False)
    	bytearray('\x00\x00\x01\x02')
	
    """
    res = bytearray(0)
    assert endian == '>' or endian == '<'
    if type(arr) == str:
        res = bytearray(map(ord, list(arr)))
    elif type(arr) == tuple or type(arr) == list:
        for el in arr:
            res.append(make_bytearray(el, length = 1, endian = '>'))
    elif type(arr) == bytearray:
        return arr
    elif type(arr) == int:
        while arr > 0:
            res.append(arr % 256)
            arr = arr / 256
    else:
        raise NotImplementedError("Cannot convert " + type(arr))
    
    # Convert the endianness and the padding:
    if endian == '<':
        res = res[::-1]
    
    pad_len = length - len(res)
    padding = bytearray(0)
    if pad_len > 0:
        padding = bytearray(pad_len)

    if tail_padding:
        return res + padding
    else:
        return padding + res
        
def start_codes(val):
    __start = {
        'Command': '\x55\xAA',
        '\x55\xAA': 'Command', 
        'Data': '\x5A\xA5',
        '\x5A\xA5': 'Data'
    }

    if __start.get(val, None) is None:
        raise NotImplementedError("Command unknown: " + str(val))
    return __start[val]

def command(val):
    __command = {
        'Open': 0x01,             # Initialization
        'Close': 0x02,            # Termination
        # ...
        'UsbInternalCheck': 0x03, # Check if the connected USB device is valid
        'ChangeBaudrate': 0x04,   # Change UART baud rate
        'SetIAPMode': 0x05,       # Enter IAP Mode. In this mode, FW Upgrade is available
        # ...
        'CmosLed': 0x12,          # Control CMOS LED
        # ...
        'GetEnrollCount': 0x20,   # Get enrolled fingerprint count
        'CheckEnrolled': 0x21,    # Check whether the specified ID is already enrolled
        'EnrollStart': 0x22,      # Start an enrollment
        'Enroll1': 0x23,          # Make 1st template for an enrollment
        'Enroll2': 0x24,          # Make 2nd template for an enrollment
        'Enroll3': 0x25,          # Make 3rd template for an enrollment. Merge three templates into one template,
        			  #    save merged template to the database 
        'IsPressFinger': 0x26,    # Check if a finger is placed on the sensor
        # ...
        'DeleteID': 0x40,         # Delete the fingerprint with the specified ID
        'DeleteAll': 0x41,        # Delete all fingerprints from the database
        # ...
        'Verify': 0x50,           # 1:1 Verification of the capture fingerprint image with the specified ID
        'Identify': 0x51,         # 1:N Identification of the capture fingerprint image with the database
        'VerifyTemplate': 0x52,   # 1:1 Verification of a fingerprint template with the specified ID
        'IdentifyTemplate': 0x53, # 1:N Identification of a fingerprint template with the database
        # ...
        'CaptureFinger': 0x60,    # Capture a fingerprint image(256x256) from the sensor
        'MakeTemplate': 0x61,     # Make template for transmission
        'GetImage': 0x61,         # Download the captured fingerprint image (256x256)
        'GetRawImage': 0x63,      # Capture & Download raw fingerprint image (320x240)
        # ...
        'GetTemplate': 0x70,      # Download the template of the specified ID 
        'SetTemplate': 0x71,      # Upload the template of the specified ID
        'GetDatabaseStart': 0x72, # Start database download, obsolete
        'GetDatabaseEnd': 0x73,   # End database download, obsolete
        # ...
        'UpgradeFirmware': 0x80,  # Not supported
        'UpgradeISOCDImage': 0x81,# Not supported
        # ...
        'Ack': 0x30,              # Acknowledge
        'Nack': 0x31              # Non-acknowledge
    }
    if type(val) == str:
        return __command.get(val)
    else:
        raise TypeError("Input should be of type 'str'")

def error(val):
    # Errors are num: value format :)
    __error = {
        0x1001: 'NACK_TIMEOUT', 		# (Obsolete) Capture timeout
        0x1002: 'NACK_INVALID_BAUDRATE',        # (Obsolete) Invalid serial baud rate
        0x1003: 'NACK_INVALID_POS',             # The specified ID is not in range[0,199]
        0x1004: 'NACK_IS_NOT_USED',             # The specified ID is not used
        0x1005: 'NACK_IS_ALREADY_USED',         # The specified ID is already in use
        0x1006: 'NACK_COMM_ERR',                # Communication error
        0x1007: 'NACK_VERIFY_FAILED',           # 1:1 Verification Failure
        0x1008: 'NACK_IDENTIFY_FAILED',         # 1:N Identification Failure
        0x1009: 'NACK_DB_IS_FULL',              # The database is full
        0x100A: 'NACK_DB_IS_EMPTY',             # The database is empty
        0x100B: 'NACK_TURN_ERR',                # (Obsolete) Invalid order of the enrollment
                                                #    (EnrollStart->Enroll1->Enroll2->Enroll3)
        0x100C: 'NACK_BAD_FINGER',              # Fingerprint is too bad
        0x100D: 'NACK_ENROLL_FAILED',           # Enrollment Failure
        0x100E: 'NACK_IS_NOT_SUPPORTED',        # The command is not supported
        0x100F: 'NACK_DEV_ERR',                 # Device error: probably Crypto-Chip is faulty (Wrong checksum ~Z)
        0x1010: 'NACK_CAPTURE_CANCELED',        # (Obsolete) Capturing was canceled
        0x1011: 'NACK_INVALID_PARAM',           # Invalid parameter
        0x1012: 'NACK_FINGER_IS_NOT_PRESSED' 	# Finger is not pressed
    }
    
    if __error.get(val, None) is not None:
        return __error[val]
    elif 0 <= val <= 199:
        return 'Duplicated ID: ' + str(val)
    else:
        return 'Unknown error code: ' + str(val) # Do we need to raise an exception?
        

def response(val):
    __response = {
        'Ack': 0x30,
        'Nack': 0x31
    }
    # __response_val = {
    #     0x30: 'ACK',
    #     0x31: 'NACK'
    # }

    if type(val) == str:
        return __response.get(val, None)
    # elif type(val) == int:      
    #     return __response_val.get(val, None)
    else:
        raise TypeError("Input should be of type 'str'")
    

    

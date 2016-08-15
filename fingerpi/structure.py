

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

comm_struct = lambda: '<BBHIH'
data_struct = lambda x: '<BBH' + str(x) + 's'
checksum_struct = lambda: '<H'

packets = {
    'Command1':  0x55,
    'Command2':  0xAA,
    'Data1':     0x5A,
    'Data2':     0xA5,
    '\x55\xAA':  'C',
    '\x5A\xA5':  'D'
}

commands = {
    'Open':             0x01,   # Initialization
    'Close':            0x02,   # Termination
    'UsbInternalCheck': 0x03,   # Check if the connected USB device is valid
    'ChangeBaudrate':   0x04,   # Change UART baud rate
    'SetIAPMode':       0x05,   # Enter IAP Mode. In this mode, FW Upgrade is available
    'CmosLed':          0x12,   # Control CMOS LED
    'GetEnrollCount':   0x20,   # Get enrolled fingerprint count
    'CheckEnrolled':    0x21,   # Check whether the specified ID is already enrolled
    'EnrollStart':      0x22,   # Start an enrollment
    'Enroll1':          0x23,   # Make 1st template for an enrollment
    'Enroll2':          0x24,   # Make 2nd template for an enrollment
    'Enroll3':          0x25,   # Make 3rd template for an enrollment. 
                                #    Merge three templates into one template,
                                #    save merged template to the database 
    'IsPressFinger':    0x26,   # Check if a finger is placed on the sensor
    'DeleteID':         0x40,   # Delete the fingerprint with the specified ID
    'DeleteAll':        0x41,   # Delete all fingerprints from the database
    'Verify':           0x50,   # 1:1 Verification of the capture fingerprint image with the specified ID
    'Identify':         0x51,   # 1:N Identification of the capture fingerprint image with the database
    'VerifyTemplate':   0x52,   # 1:1 Verification of a fingerprint template with the specified ID
    'IdentifyTemplate': 0x53,   # 1:N Identification of a fingerprint template with the database
    'CaptureFinger':    0x60,   # Capture a fingerprint image(256x256) from the sensor
    'MakeTemplate':     0x61,   # Make template for transmission
    'GetImage':         0x62,   # Download the captured fingerprint image (256x256)
    'GetRawImage':      0x63,   # Capture & Download raw fingerprint image (32'\x240)
    'GetTemplate':      0x70,   # Download the template of the specified ID 
    'SetTemplate':      0x71,   # Upload the template of the specified ID
    'GetDatabaseStart': 0x72,   # Start database download, obsolete
    'GetDatabaseEnd':   0x73,   # End database download, obsolete
    'UpgradeFirmware':  0x80,   # Not supported
    'UpgradeISOCDImage':0x81,   # Not supported
    'Ack':              0x30,   # Acknowledge
    'Nack':             0x31    # Non-acknowledge
}

errors = {
    0x1001: 'NACK_TIMEOUT',                 # (Obsolete) Capture timeout
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
    0x1012: 'NACK_FINGER_IS_NOT_PRESSED',   # Finger is not pressed
}

responses = {
    'Ack':  0x30,
    'Nack': 0x31,
    0x30:   'Ack',
    0x31:   'Nack'
}


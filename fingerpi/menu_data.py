import struct 
import fingerpi as fp

MENU = "menu"
COMMAND = "command"
EXITMENU = "exitmenu"

menu_data = {
    'title': "GT-511C3 UART", 'type': MENU, 'subtitle': "Please select an option...",
    'options':[
        { 'title': "Initialize", 'type': COMMAND, 'command': 'C.Initialize()' },
        { 'title': "Open", 'type': COMMAND, 'command': 'C.Open()' },
        { 'title': "LED on/off", 'type': COMMAND, 'command': '' },
        { 'title': "Enroll Sequence", 'type': COMMAND, 'command': '' },
        { 'title': "All Commands", 'type': MENU, 'subtitle': "Please select an option...", 
        'options': [
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Close", 'type': COMMAND, 'command': '' },
            { 'title': "UsbInternalCheck", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
            { 'title': "Open", 'type': COMMAND, 'command': '' },
        ]},
    ]
}

class Commands():
    ## Every method has to return `status` array of size 2
    def __init__(self):
        self.f = None
        self.status = 'Uninitialized...'
        self.open = False
        self.led = None
        
    def Initialize(self):
        status = 'Initialized'
        if self.f is not None:
            return ['Already initialized...', status]
        self.f = fp.FingerPi()

        if self.f is None:
            raise Exception('Could not initialize FingerPi()')
        return ['', status]

    def Open(self):
        if self.open:
            return ['Already open...', None]
        ## Bottom status format:
        # 'Status: Closed' or
        # 'Status: Open\t`Baudrate`\t`firmware ver.`\t`device serial number`'
        if self.f is None:
            raise Exception('Could not Open() - FingerPi() not initialized')
            # return ['Error: Please initialize the device first!', None]
        self.open = True # Show the default status iff NOT initialized!
        status = [None, None]
        response = self.f.Open(extra_info = True, check_baudrate = True)
        if response[0]['ACK']:
            data = struct.unpack('II16B', response[1]['Data'])
            serial_num = bytearray(data[2:])
            status[0] = ''
            status[1] = 'Open; Baudrate: %s; Firmware ver.: %s; Serial #: %s'%(
                response[0]['Parameter'],
                data[0],
                str(serial_num).encode('hex')
            )
            self.status = status[1]
        return status

## TODO: Commands in the menu_data?
def processrequest(menu):
    status = [None, None] # 0: Top, 1: Bottom
    assert menu['type'] == COMMAND
    # Check if the Commands object is created
    try:
        C
    except:
        global C
        C = Commands()
    # Run the commands
    try:
        status = eval(menu['command'])
        # We don't want to change the bottom status that often!
        if C.open or status[1] == None:
            status[1] = C.status
    except Exception as e:
        # e = sys.exc_info()
        # raise e
        # status = '\n\t'.join(map(str, e))
        # status = 'Error: ' + str(e[1])
        status = ['Error: (while running ' + menu['title'] + ') ' + str(e), C.status]

    status = map(str, status)
    return status


import struct 
import fingerpi as fp

import curses

from time import sleep
from threading import Timer

class RepeatingTimer(object):
    def __init__(self, interval, f, *args, **kwargs):
        self.interval = interval
        self.f = f
        self.args = args
        self.kwargs = kwargs

        self.timer = None

    def callback(self):
        self.f(*self.args, **self.kwargs)
        self.start()

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.timer = Timer(self.interval, self.callback)
        self.timer.start()

port = '/dev/ttyAMA0'
        
MENU = "menu"
COMMAND = "command"
EXITMENU = "exitmenu"

menu_data = {
    'title': "GT-511C3 UART", 'type': MENU, 'subtitle': "Please select an option...",
    'options':[
        { 'title': "Initialize", 'type': COMMAND, 'command': 'Initialize' },
        { 'title': "Open", 'type': COMMAND, 'command': 'Open' },
        { 'title': "Blink", 'type': COMMAND, 'command': 'Blink' },
        { 'title': "Enroll Sequence", 'type': COMMAND, 'command': '' },
        { 'title': "All Commands", 'type': MENU, 'subtitle': "Please select an option...", 
        'options': [
            { 'title': "Open", 'type': COMMAND, 'command': 'Open' },
            { 'title': "Close", 'type': COMMAND, 'command': 'Close' },
            { 'title': "USB Internal Check", 'type': COMMAND, 'command': 'UsbInternalCheck' },
            { 'title': "LED on/off", 'type': COMMAND, 'command': 'CmosLed' },
            { 'title': "Change Baudrate", 'type': COMMAND, 'command': 'ChangeBaudrate' },
            { 'title': "Get Enroll Count", 'type': COMMAND, 'command': 'GetEnrollCount' },
            { 'title': "Check Enrolled", 'type': COMMAND, 'command': 'CheckEnrolled' },
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
        
    def Initialize(self, *args):
        status = 'Initialized'
        if self.f is not None:
            return ['Already initialized...', status]
        self.f = fp.FingerPi(port = port)

        if self.f is None:
            raise Exception('Could not initialize FingerPi()')
        return ['', status]

    def Open(self, *args):
        if self.open:
            return ['Already open...', None]
        ## Bottom status format:
        # 'Status: Closed' or
        # 'Status: Open\t`Baudrate`\t`firmware ver.`\t`device serial number`'
        if self.f is None:
            raise Exception('Not initialized!')
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
        else:
            raise Exception('Received NACK')
        return status

    def LED(self, *args, **kwargs): # Need screen for popup window
        if self.led is None:
            self.led = True
        else:
            self.led = not self.led
        if kwargs.get('led', None) is not None:
            self.led = kwargs['led']
        response = self.f.CmosLed(self.led)
        # response = [{'ACK': True}]
        if not response[0]['ACK']:
            raise Exception('Received NACK')

        if len(args) > 0:
            # Screen is given, no point returning
            args[0].addstr(2, 2, 'LED is set to ' + (' ON' if self.led else 'OFF'))
            args[0].refresh()
            return ['', None]
        else:
            return ['LED is set to ' + ('ON' if self.led else 'OFF'), None]

    def Blink(self, *args):
        if not self.open:
            raise Exception('Not open!')
        screen = args[0]
        y, x = screen.getmaxyx()
        screen.border(0)
        screen.addstr(0, 1, 'Press any button to stop...'[:x-2], curses.A_STANDOUT)

        t = RepeatingTimer(0.5, self.LED, screen)
        t.start()

        screen.refresh()
        inp = screen.getch()
        if inp:
            t.cancel()
            self.LED(led = False)
            self.led = False
            
        return ['', None]


## TODO: Commands in the menu_data?
def processrequest(menu, *args):
    global C
    ## Need screen to show directions!!!
    scr = args[0]
    y,x = scr.getmaxyx()
    screen = scr.derwin(y / 4, x / 2, y * 3 / 4, x / 4)
    screen.clear()
    status = [None, None] # 0: Top, 1: Bottom
    assert menu['type'] == COMMAND
    # Check if the Commands object is created
    try:
        C
    except:
        C = Commands()
    # Run the commands
    try:
        status = eval('C.'+menu['command'])(screen) # Give it the subwindow, just in case!
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


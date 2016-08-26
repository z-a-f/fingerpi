import struct 

import curses

from time import sleep
from threading import Timer

from .exceptions import *
import fingerpi as fp

class RepeatingTimer(object):
    def __init__(self, interval, f, *args, **kwargs):
        self.interval = interval
        self._f = f
        self.args = args
        self.kwargs = kwargs

        self.timer = None

    def callback(self):
        self._f(*self.args, **self.kwargs)
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

BAUDRATES = [9600, 14400, 19200, 28800, 38400, 56000, 57600, 115200]

menu_data = {
    'title': "GT-511C3 UART", 'type': MENU, 'subtitle': "Please select an option...",
    'options':[
        { 'title': "Initialize", 'type': COMMAND, 'command': 'Initialize' },
        { 'title': "Open", 'type': COMMAND, 'command': 'Open' },
        { 'title': "Change Baudrate", 'type': MENU, 'subtitle': 'Please select and option...',
        'options': [ 
            { 'title': str(x), 'type': COMMAND, 'command': 'ChangeBaudrate(%d)'%x } for x in BAUDRATES
        ]},
        { 'title': "Blink", 'type': COMMAND, 'command': 'Blink' },
        { 'title': "Enroll Sequence", 'type': COMMAND, 'command': '' },
        { 'title': "All Commands", 'type': MENU, 'subtitle': "Please select an option...", 
        'options': [
            { 'title': "Open", 'type': COMMAND, 'command': 'Open' },
            { 'title': "Close", 'type': COMMAND, 'command': 'Close' },
            { 'title': "USB Internal Check", 'type': COMMAND, 'command': 'UsbInternalCheck' },
            { 'title': "LED on/off", 'type': COMMAND, 'command': 'CmosLed' },
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
        self._f = None
        self.status = 'Uninitialized...'
        self._led = None

        self.open = False
        self._status_template = r'%s; Baudrate: %s; Firmware ver.: %s; Serial #: %s'
        self._baudrate = 'N/A'
        self._firmware = 'N/A'
        self._serial_no = 'N/A'

    def _update_status(self):
        if self.open: 
            __status = 'Open'
        else:
            __status = 'Closed'
        self.status = self._status_template % (
            __status,
            str(self._baudrate),
            str(self._firmware),
            str(self._serial_no)
        )
        
    def Initialize(self, *args):
        if self._f is not None:
            raise AlreadyInitializedError('This device is already initialized')

        try:
            self._f = fp.FingerPi(port = port)
        except IOError as e:
            raise PortError(str(e))
        # self._status = 'Initialized' # Change that to `closed`
        self._update_status()
        return ['', None]

    def Open(self, *args):
        if self.open:
            raise AlreadyOpenError('This device is already open')
        if self._f is None:
            raise NotInitializedError('Please, initialize first!')

        response = self._f.Open(extra_info = True, check_baudrate = True)
        if response[0]['ACK']:
            data = struct.unpack('II16B', response[1]['Data'])
            # serial_number = bytearray(data[2:])

            self._baudrate = response[0]['Parameter']
            self._firmware = data[0]
            self._serial_no = str(bytearray(data[2:])).encode('hex')

            self.open = True # Show the default status iff NOT initialized!
            self._update_status()
        else:
            raise NackError(response[0]['Parameter'])
        return [None, None]

    def Blink(self, *args):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        screen = args[0]
        y, x = screen.getmaxyx()
        screen.border(0)
        screen.addstr(0, 1, 'Press any button to stop...'[:x-2], curses.A_STANDOUT)

        t = RepeatingTimer(0.5, self.CmosLed, screen)
        t.start()

        screen.refresh()
        inp = screen.getch()
        if inp:
            t.cancel()
            self.CmosLed(led = False)
            self._led = False
            
        return ['', None]

    ####################################################################
    ## All (other) commands:

    def Close(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        response = self._f.Close()
        if not response[0]['ACK']:
            raise NackError(response[0]['Parameter'])
        self.open = False
        self._update_status()
        return [None, None]

    def UsbInternalCheck(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        response = self._f.UsbInternalCheck()
        if reponse[0]['ACK']:
            return ['USB Internal Check returned: ' + str(response[0]['Parameter']), None]
        else:
            raise NackError(response[0]['Parameter'])

    def CmosLed(self, *args, **kwargs): # Need screen for popup window
        # Several modes of operation:
        # 1) If no argument is given - toggle LED
        # 2) If named boolean argument `led` is given - set the led to specified value
        # 3) If positional argument is given - don't return the result, show the result on a separate curses.window
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        if self._led is None:
            self._led = True
        else:
            self._led = not self._led

        if kwargs.get('led', None) is not None:
            self._led = kwargs['led']
        response = self._f.CmosLed(self._led)
        # response = [{'ACK': True}]
        if response[0]['ACK']:
            if len(args) > 0:
                # Screen is given, show a message
                args[0].addstr(2, 2, 'LED is set to ' + (' ON' if self._led else 'OFF'))
                args[0].refresh()
                return ['', None]
            else:
                # Screen is not given, return the message
                return ['LED is set to ' + ('ON' if self._led else 'OFF'), None]
        else:
            raise NackError(response[0]['Parameter'])

    def ChangeBaudrate(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        rate = int(args[0])
        if not (9600 <= rate <= 115200):
            raise ValueError('Incorrect baudrate: ' + str(args[0]))
        reponse = self._f.ChangeBaudrate(args[0])
        if response[0]['ACK']:
            self._baudrate = str(rate)
            self._update_status()
            return [None, None]
        else:
            raise NackError("Couldn't change baudrate - rerun `Open` to identify")





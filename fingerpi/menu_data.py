import struct 

import curses

from time import sleep
from threading import Timer

import pickle

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

BAUDRATES = [9600,
             # 14400,
             19200,
             # 28800,
             38400,
             # 56000,
             57600,
             115200]
## NOTE: `curses.window` is passed as the first argument to every function!
menu_data = {
    'title': "GT-511C3 UART", 'type': MENU, 'subtitle': "Please select an option...",
    'options':[
        { 'title': "Initialize", 'type': COMMAND, 'command': 'Initialize', 'kwargs':{} },
        { 'title': "Open", 'type': COMMAND, 'command': 'Open', 'kwargs':{} },
        { 'title': "Change Baudrate", 'type': MENU, 'subtitle': 'Please select and option...',
        'options': [ 
            { 'title': str(x), 'type': COMMAND, 'command': 'ChangeBaudrate', 'kwargs': {'baudrate': x} } for x in BAUDRATES
        ]},
        { 'title': "Blink", 'type': COMMAND, 'command': 'Blink', 'kwargs':{} },
        { 'title': "Enroll Sequence", 'type': COMMAND, 'command': '', 'kwargs':{} },
        { 'title': "All Commands", 'type': MENU, 'subtitle': "Please select an option...", 
        'options': [
            { 'title': "Open", 'type': COMMAND, 'command': 'Open', 'kwargs':{} },
            { 'title': "Close", 'type': COMMAND, 'command': 'Close', 'kwargs':{} },
            { 'title': "USB Internal Check", 'type': COMMAND, 'command': 'UsbInternalCheck', 'kwargs':{} },
            { 'title': "LED on/off", 'type': COMMAND, 'command': 'CmosLed', 'kwargs':{} },
            { 'title': "Get Enroll Count", 'type': COMMAND, 'command': 'GetEnrollCount', 'kwargs':{} },
            { 'title': "Check Enrolled", 'type': COMMAND, 'command': 'CheckEnrolled', 'kwargs':{} },
            { 'title': "Start Enrollment", 'type': COMMAND, 'command': 'EnrollStart', 'kwargs':{} },
            { 'title': "Is Finger Pressed?", 'type': COMMAND, 'command': 'IsPressFinger', 'kwargs':{} },
            { 'title': "Get Image", 'type': COMMAND, 'command': 'GetImage', 'kwargs':{} },
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
        
    def Initialize(self, *args, **kwargs):
        if self._f is not None:
            raise AlreadyInitializedError('This device is already initialized')

        try:
            self._f = fp.FingerPi(port = port)
        except IOError as e:
            raise PortError(str(e))
        # self._status = 'Initialized' # Change that to `closed`
        self._update_status()
        return [None, None]

    def Open(self, *args, **kwargs):
        if self.open:
            raise AlreadyOpenError('This device is already open')
        if self._f is None:
            raise NotInitializedError('Please, initialize first!')

        # self._f.serial.reset_input_buffer()

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

    def Blink(self, *args, **kwargs):
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
        rate = int(kwargs['baudrate'])
        if not (9600 <= rate <= 115200):
            raise ValueError('Incorrect baudrate: ' + str(args[0]))
        response = self._f.ChangeBaudrate(rate)
        if response[0]['ACK']:
            self._baudrate = str(rate)
            self._update_status()
            return [None, None]
        else:
            self.open = False
            self._baudrate = 'Unknown'
            self._update_status()
            raise NackError("Couldn't change baudrate: " + str(response[0]['Parameter']))

    def GetEnrollCount(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        response = self._f.GetEnrollCount()
        if response[0]['ACK']:
            return ['Number of enrolled fingerprints: ' + str(response[0]['Parameter']), None]
        else:
            raise NackError(response[0]['Parameter'])

    def CheckEnrolled(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        screen = args[0]
        y, x = screen.getmaxyx()
        # screen.border(0)
        # screen.addstr(0, 1, 'Enter the ID to check, or empty field to exit...'[:x-2], curses.A_STANDOUT)
        curses.echo()
        while True:
            screen.addstr(2, 2, '>>> ')
            screen.clrtoeol()
            screen.border(0)
            screen.addstr(0, 1, 'Enter the ID to check, or empty field to exit...'[:x-2], curses.A_STANDOUT)
            ID = screen.getstr(2, 6)
            if ID.isdigit():
                response = self._f.CheckEnrolled(int(ID))
                if response[0]['ACK']:
                    screen.addstr(3, 2, 'ID in use!')
                    screen.clrtoeol()
                else:
                    screen.addstr(3, 2, response[0]['Parameter'])
                    screen.clrtoeol()
            elif ID.isalnum():
                curses.noecho()
                raise ValueError('Non-numeric value found!')
            else:
                break
        curses.noecho()
        return [None, None]

    def IsPressFinger(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        response = self._f.IsPressFinger()
        if response[0]['ACK']:
            if response[0]['Parameter'] == 0:
                # Finger is pressed
                return [True, None]
            else:
                return [False, None]
        else:
            raise NackError(response[0]['Parameter'])

    def EnrollStart(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        screen = args[0]
        y, x = screen.getmaxyx()
        # screen.border(0)
        # screen.addstr(0, 1, 'Enter the ID to check, or empty field to exit...'[:x-2], curses.A_STANDOUT)
        curses.echo()
        ret = [False, None]
        while True: 
            screen.addstr(2, 2, '>>> ')
            screen.clrtoeol()
            screen.border(0)
            screen.addstr(0, 1, 'Enter a new ID for enrollment, or empty field to cancel...'[:x-2], curses.A_STANDOUT)
            ID = screen.getstr(2, 6)
            if ID.isdigit():
                response = self._f.EnrollStart(int(ID))
                if response[0]['ACK']:
                    # screen.addstr(3, 2, 'ID in use!')
                    # screen.clrtoeol()
                    ret[0] = 'Enrollment of ID {0:d} started'.format(response[0]['Parameter'])
                    break
                else:
                    screen.addstr(3, 2, response[0]['Parameter'])
                    screen.clrtoeol()
            elif ID.isalnum():
                curses.noecho()
                raise ValueError('Non-numeric value found!')
            else:
                break
        curses.noecho()
        return ret

    def Enroll1(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        response = self._f.Enroll1()
        if not response[0]['ACK']:
            if response[0]['ACK'] in errors:
                err = response[0]['ACK']
            else:
                err = 'Duplicate ID: ' + str(response[0]['ACK'])
            raise NackError(err)
        return [None, None]

    def Enroll2(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        response = self._f.Enroll1()
        if not response[0]['ACK']:
            if response[0]['ACK'] in errors:
                err = response[0]['ACK']
            else:
                err = 'Duplicate ID: ' + str(response[0]['ACK'])
            raise NackError(err)
        return [None, None]

    def Enroll3(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        response = self._f.Enroll1()
        if not response[0]['ACK']:
            if response[0]['ACK'] in errors:
                err = response[0]['ACK']
            else:
                err = 'Duplicate ID: ' + str(response[0]['ACK'])
            raise NackError(err)
        if self._f.save:
            return [str(len(response[1]['Data'])) + ' bytes received... And purged!', None]
        return [None, None]

    def DeleteID(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        screen = args[0]
        y, x = screen.getmaxyx()
        # screen.border(0)
        # screen.addstr(0, 1, 'Enter the ID to check, or empty field to exit...'[:x-2], curses.A_STANDOUT)
        curses.echo()
        ret = [False, None]
        while True: 
            screen.addstr(2, 2, '>>> ')
            screen.clrtoeol()
            screen.border(0)
            screen.addstr(0, 1, 'Enter an ID to delete, or empty field to cancel...'[:x-2], curses.A_STANDOUT)
            ID = screen.getstr(2, 6)
            if ID.isdigit():
                response = self._f.DeleteID(int(ID))
                if response[0]['ACK']:
                    # screen.addstr(3, 2, 'ID in use!')
                    # screen.clrtoeol()
                    ret[0] = 'ID {0:d} deleted'.format(ID)
                    break
                else:
                    screen.addstr(3, 2, response[0]['Parameter'])
                    screen.clrtoeol()
            elif ID.isalnum():
                curses.noecho()
                raise ValueError('Non-numeric value found!')
            else:
                break
        curses.noecho()
        return ret

    def DeleteAll(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        response = self._f.DeleteAll()
        if not response[0]['ACK']:
            raise NackError(response[0]['Parameter'])
        return [None, None]

    def Verify(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        screen = args[0]
        y, x = screen.getmaxyx()
        # screen.border(0)
        # screen.addstr(0, 1, 'Enter the ID to check, or empty field to exit...'[:x-2], curses.A_STANDOUT)
        curses.echo()
        ret = [False, None]
        while True: 
            screen.addstr(2, 2, '>>> ')
            screen.clrtoeol()
            screen.border(0)
            screen.addstr(0, 1, 'Enter an ID to verify, or empty field to cancel...'[:x-2], curses.A_STANDOUT)
            ID = screen.getstr(2, 6)
            if ID.isdigit():
                response = self._f.Verify(int(ID))
                if response[0]['ACK']:
                    # screen.addstr(3, 2, 'ID in use!')
                    # screen.clrtoeol()
                    ret[0] = 'ID {0:d} verified'.format(ID)
                    break
                else:
                    screen.addstr(3, 2, response[0]['Parameter'])
                    screen.clrtoeol()
            elif ID.isalnum():
                curses.noecho()
                raise ValueError('Non-numeric value found!')
            else:
                break
        curses.noecho()
        return ret

    def Identify(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        response = self._f.Identify()
        if not response[0]['ACK']:
            raise NackError(response[0]['Parameter'])
        return [response[0]['Parameter'], None]

    def CaptureFinger(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')

        best_image = 1
        if len(args) > 0:
            best_image = args[0]
        response = self._f.CaptureFinger(best_image)
        if not response[0]['ACK']:
            raise NackError(response[0]['Parameter'])
        return [None, None]

    def GetImage(self, *args, **kwargs):
        if not self.open:
            raise NotOpenError('Please, open the port first!')
        response = self._f.GetImage()
        if not response[0]['ACK']:
            raise NackError(response[0]['Parameter'])

        screen = args[0]
        y, x = screen.getmaxyx()
        # screen.border(0)
        # screen.addstr(0, 1, 'Enter the ID to check, or empty field to exit...'[:x-2], curses.A_STANDOUT)
        curses.echo()
        ret = [False, None]
        while True: 
            screen.addstr(2, 2, '>>> ')
            screen.clrtoeol()
            screen.border(0)
            screen.addstr(0, 1, 'Enter an the path to save the file to, or empty field to cancel...'[:x-2], curses.A_STANDOUT)
            ID = screen.getstr(2, 6)
            if len(ID) > 0:
                data = response[1]['Data']
                # Try saving the file
                # try:
                # fl = open(ID, 'w')
                # fl.write(response[1]['Data'])
                # fl.close()
                # except IOError as e:
                #     curses.noecho()
                #     fl.close()
                #    raise IOError('Could not write file! ' + str(e))
                with open('ID', 'w') as f:
                    pickle.dump(data, f)
                break
            else:
                break
        curses.noecho()
        return ret




















        
        

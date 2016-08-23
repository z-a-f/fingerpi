#!/usr/bin/env python

# from __future__ import print_function
import curses

import fingerpi as fp

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

   
def cprint(color, message):
    # print color in bcolors
    print (color + message + bcolors.ENDC)


def status(window, commands, message = '', start_row = 16, start_col = 0):
    window.addstr(start_row, start_col, message, curses.A_STANDOUT)
    window.clrtobot()
    window.refresh()

def items(window, selection = None, start_idx = 3):
    if selection is None:
        selection = start_idx
    assert selection >= start_idx

    
    
    
def menu(window):    
    window.addstr(0, 0,'Please make a selection:')

    # window.addstr(2, 0, '(o) Send `open` command')
    window.addstr(3, 0, '(b) Change baudrate')
    # window.addstr(3, 0, '(l) Turn LED on/off')
    window.addstr(4, 0, '(g) Get enroll count')
    window.addstr(5, 0, '(c) Check if ID is enrolled')
    window.addstr(6, 0, '(E) Enroll fingerprint')
    # window.addstr(4, 0, '(c) Send `close` command')

    window.addstr(8, 0, '(q) Quit')
    
    while True:
        # curses.echo()
        c = window.getch()
        # curses.noecho()
        if c == ord('q'):
            break
        elif c > 255:
            # window.addstr(16, 0, 'Pressed\nsomething')
            status(window, 'Pressend something!!!\n!!\n!\nsd')
        else:
            # window.addstr(16, 0, 'Pressed '+chr(c), curses.A_STANDOUT)
            status(window, 'Pressed ' + chr(c))
        # window.refresh()
    
if __name__ == '__main__':
    fing = fp.FingerPi()
    fing.Open()
    commands = [
        {'key':'b', 'message': 'Change baudrate', 'command': }
    ]

    curses.wrapper(menu)

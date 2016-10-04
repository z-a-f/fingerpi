
# Topmenu and the submenus are based of the example found at this location http://blog.skeltonnetworks.com/2010/03/python-curses-custom-menu/
# The rest of the work was done by Matthew Bennett and he requests you keep these two mentions when you reuse the code :-)
# Basic code refactoring by Andrew Scheller

## NOTE: We catch UnboundLocalError exceptions in the `processrequest`!!!

## Usage: curses.wrapper(processmenu,menu_data) # menu_data is the menu data structure

import curses

## These should be the same as in the menu_data!!!
# MENU = "menu"
# COMMAND = "command"
# EXITMENU = "exitmenu"

## processrequest is defined in the `menu_data`
from .menu_data import MENU, COMMAND, EXITMENU # processrequest, 
from .menu_data import Commands

from .exceptions import *

# This function displays the appropriate menu and returns the option selected
def runmenu(screen, menu, parent, status_mid = '', status_bottom = ''):
    ## Need to somehow make these global
    h = curses.color_pair(1) #h is the coloring for a highlighted menu option
    n = curses.A_NORMAL #n is the coloring for a non highlighted menu option

    mid_status_from_the_bottom = 3 # How manu rows from the bottom would a status region start?

    # work out what text to display as the last menu option
    if parent is None:
        lastoption = "Exit"
    else:
        lastoption = "Return to {0!s} menu".format(parent['title'])

    optioncount = len(menu['options']) # how many options in this menu

    pos=0 #pos is the zero-based index of the hightlighted menu option. Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what opt$
    oldpos=None # used to prevent the screen being redrawn every time
    x = None #control for while loop, let's you scroll through options until return key is pressed then returns pos to program

    rows, cols = screen.getmaxyx()

    # connection_status = 'Closed'
    # response_status = ''

    # Loop until return key is pressed
    while x !=ord('\n'):
        if pos != oldpos or x == curses.KEY_RESIZE: # In case window is resized, redraw everything!
            if x == curses.KEY_RESIZE: 
                screen.clear() # Clear borders and stuff!
                rows, cols = screen.getmaxyx() # Update the rows and colms
            else:
                oldpos = pos

            # screen.border(0)
            screen.addstr(2,2, menu['title'], curses.A_STANDOUT) # Title for this menu
            screen.addstr(4,2, menu['subtitle'], curses.A_BOLD) #Subtitle for this menu

            # Display all the menu items, showing the 'pos' item highlighted
            for index in range(optioncount):
                textstyle = n
                if pos==index:
                    textstyle = h
                screen.addstr(5+index,4, "{0:d} - {1!s}".format(index+1, menu['options'][index]['title']), textstyle)
            # Now display Exit/Return at bottom of menu
            textstyle = n
            if pos==optioncount:
                textstyle = h
            screen.addstr(5+optioncount,4, "{0:d} - {1!s}".format(optioncount+1, lastoption), textstyle)

            # Add the status of the connection and of the response
            screen.clrtobot()
            screen.border(0) # Clear to bottom clears the borders as well :(
            if status_mid is None or status_mid == 'None':
                status_mid = ''
                screen.addstr(rows - mid_status_from_the_bottom, 4, status_mid)
            else:
                # Divide in multiple lines + skip 4 columns from both sides
                # idx = 0 # This makes sure that we don't go below the screen (if dividing the string into rows)
                #while len(status_mid) > 0 and idx < mid_status_from_the_bottom:
                screen.addstr(rows - mid_status_from_the_bottom, 4, status_mid[:cols - 8])
            
                #status_mid = status_mid[cols-8:]
                #idx += 1

            if status_bottom is not None:
                screen.clrtoeol()
                screen.border(0) # Clear to bottom clears the borders as well :(
                bot = 'Status: ' + status_bottom
                screen.addstr(rows - 1, 4, bot[:cols-8])
            
            #else:
            screen.refresh()
            # finished updating screen

        x = screen.getch() # Gets user input

        # What is user input?
        if x >= ord('1') and x <= optioncount+1:#ord(str(optioncount+1)):
            pos = x - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
        elif x == 258: # down arrow
            if pos < optioncount:
                pos += 1
            else: pos = 0
        elif x == 259: # up arrow
            if pos > 0:
                pos += -1
            else: pos = optioncount
        # elif x == curses.KEY_RESIZE:
        #     # raise NotImplementedError('Resizing is not implemented yet - sorry, will get to it eventually!')
        #     screen.refresh()
        #     rows, cols = screen.getmaxyx()

    # return index of the selected item
    return pos

## TODO: Commands in the menu_data?
def processrequest(menu, *args):
    global C # This will hold the `Commands` object.
    ## Need screen to show directions!!!
    scr = args[0]
    y,x = scr.getmaxyx()
    screen = scr.derwin(y / 4, x / 2, y * 3 / 4, x / 4)
    screen.clear()
    status = [None, None] # 0: Top, 1: Bottom
    assert menu['type'] == COMMAND
    # Check if the Commands object is already created
    try:
        C
    except:
        C = Commands()
    # Run the commands
    try:
        status = eval('C.'+menu['command'])(screen, **menu['kwargs']) # Give it the subwindow, just in case!
        # We don't want to change the bottom status that often!
        if C.open or status[1] == None:
            status[1] = C.status
    # except UnboundLocalError as e:
    #     # e = sys.exc_info()
    #     # raise e
    #     # status = '\n\t'.join(map(str, e))
    #     # status = 'Error: ' + str(e[1])
    #     status = ['Error: (while running ' + menu['title'] + ') ' + str(e), C.status]
    except PortError as e:
        status = ['Port Error: ' + str(e), C.status]
    except (AlreadyError, NotYetError) as e:
        status = ['Error: ' + str(e), C.status]
    except NackError as e:
        status = ['Not acknoledged: ' + str(e), C.status]
    # except ValueError as e:
    #    status = ['Error: ' + str(e), C.status]
        

    status = map(str, status)
    return status

# This function calls showmenu and then acts on the selected item
def processmenu(screen, menu, parent=None, status_bottom = 'Uninitialized...'):
    curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.curs_set(0)
    status_mid = ''
    optioncount = len(menu['options'])
    exitmenu = False
    # response = None
    while not exitmenu: #Loop until the user exits the menu
        getin = runmenu(screen, menu, parent, status_mid, status_bottom)
        if getin == optioncount:
            exitmenu = True
        elif menu['options'][getin]['type'] == COMMAND:
            screen.clear() #clears previous screen
            status_mid, status_bottom = processrequest(menu['options'][getin], screen) # Add additional space
            ## Show the updated status
            screen.clear() #clears previous screen on key press and updates display based on pos
        elif menu['options'][getin]['type'] == MENU:
            screen.clear() #clears previous screen on key press and updates display based on pos
            processmenu(screen, menu['options'][getin], menu, status_bottom) # display the submenu, and make sure the status is persistent
            screen.clear() #clears previous screen on key press and updates display based on pos
        elif menu['options'][getin]['type'] == EXITMENU:
            exitmenu = True


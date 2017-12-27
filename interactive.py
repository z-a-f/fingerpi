#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import curses #curses is the interface for capturing key presses on the menu, os launches the files

import fingerpi as fp
from gui.interactive import processmenu
from gui.menu_data import *

# Main program
curses.wrapper(processmenu,menu_data) # For the error handling
curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
os.system('clear')

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import curses #curses is the interface for capturing key presses on the menu, os launches the files

import fingerpi as fp
from fingerpi.interactive import processmenu
from fingerpi.menu_data import *

# Main program
curses.wrapper(processmenu,menu_data) # For the error handling
curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
os.system('clear')

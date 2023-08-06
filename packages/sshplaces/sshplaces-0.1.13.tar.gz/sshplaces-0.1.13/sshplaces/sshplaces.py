#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Topmenu and the submenus are based of the example found at this location http://blog.skeltonnetworks.com/2010/03/python-curses-custom-menu/
# The rest of the work was done by Matthew Bennett and he requests you keep these two mentions when you reuse the code :-)
# Basic code refactoring by Andrew Scheller

# BACKWARD compatibility - START
# For backward compatibility print and input statements:
from __future__ import print_function
if hasattr(__builtins__, 'raw_input'):
    input = raw_input
# BACKWARD compatibility - END



from time import sleep
import shutil
import sys
import getopt
import curses, os #curses is the interface for capturing key presses on the menu, os launches the files

screen = ''
h = ''
n = ''

def init_screen ():
  global screen, h, n
  screen = curses.initscr() #initializes a new window for capturing key presses
  curses.noecho() # Disables automatic echoing of key presses (prevents program from input each key twice)
  curses.cbreak() # Disables line buffering (runs each key as it is pressed rather than waiting for the return key to pressed)
  curses.start_color() # Lets you use colors when highlighting selected menu option
  screen.keypad(1) # Capture input from keypad

  # Change this to use different colors when highlighting
  curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE) # Sets up color pair #1, it does black text with white background
  h = curses.color_pair(1) #h is the coloring for a highlighted menu option
  n = curses.A_NORMAL #n is the coloring for a non highlighted menu option


MENU = "menu"
COMMAND = "command"
INTERNAL = "internal"
EXITMENU = "exitmenu"
configfile="servers.yaml"
config = ''
process = ''
debug_line = ''
debug = 0

#from classes.config import * 
from classes.Config import Config 
from classes.Process import Process
from version import *

menu_data = {
  'title': "ssh places "  , 'type': MENU, 'subtitle': "Please select below ..",
  'options':[
        { 'title': "help", 'type': INTERNAL, 'command': 'help' },
        { 'title': "show configured servers", 'type': INTERNAL, 'command': 'show_config' },
#        { 'title': "server group A", 'type': MENU, 'subtitle': "Select host ",
#        'options': [
#          {'title': "server1", 'type': COMMAND, 'command': 'ssh server1.example' },
#          {'title': "server2", 'type': COMMAND, 'command': 'ssh server2.example' },
#        ]
#        },

  ]
}

def redraw_screen (menu, parent, optioncount, lastoption):

  try:
    pos = optioncount
    oldpos = pos
    screen.border(0)
    screen.addstr(2,2, menu['title'], curses.A_STANDOUT) # Title for this menu
    screen.addstr(4,2, menu['subtitle'], curses.A_BOLD) #Subtitle for this menu

    # Display all the menu items, showing the 'pos' item highlighted
    for index in range(optioncount):
      textstyle = n
      if pos==index:
        textstyle = h
      screen.addstr(5+index,4, "%d - %s" % (index+1, menu['options'][index]['title']), textstyle)
    # Now display Exit/Return at bottom of menu
    textstyle = n
    if pos==optioncount:
      textstyle = h
    screen.addstr(5+optioncount,4, "%d - %s" % (optioncount+1, lastoption), textstyle)
    screen.refresh()
  except curses.error:
    pass




# This function displays the appropriate menu and returns the option selected
def runmenu(menu, parent):
  global menu_data, debug_line

  # work out what text to display as the last menu option
  if parent is None:
    lastoption = "Exit"
  else:
    lastoption = "Return to %s menu" % parent['title']

  optioncount = len(menu['options']) # how many options in this menu

  pos=0 #pos is the zero-based index of the hightlighted menu option. Every time runmenu is called, position returns to 0, when runmenu ends the position is returned and tells the program what opt$

  pos = optioncount

  oldpos=None # used to prevent the screen being redrawn every time
  x = None #control for while loop, let's you scroll through options until return key is pressed then returns pos to program

  # Loop until return key is pressed
  screen.addstr(2,50, 'sshplaces version: ' + VERSION, n) # Title for this menu
  screen.addstr(3,50, 'config: ' + configfile, n) # Title for this menu
  if debug == 1 and debug_line:
    screen.addstr(1,2, 'debug: ' + debug_line, n) # Title for this menu
  while x !=ord('\n'):
    if pos != oldpos:
      oldpos = pos
      screen.border(0)
      screen.addstr(2,2, menu['title'], curses.A_STANDOUT) # Title for this menu
      screen.addstr(4,2, menu['subtitle'], curses.A_BOLD) #Subtitle for this menu

      # Display all the menu items, showing the 'pos' item highlighted
      for index in range(optioncount):
        textstyle = n
        if pos==index:
          textstyle = h
        try:
          screen.addstr(5+index,4, "%d - %s" % (index+1, menu['options'][index]['title']), textstyle)
        except curses.error:
          pass
      # Now display Exit/Return at bottom of menu
      textstyle = n
      if pos==optioncount:
        textstyle = h
      try:
        screen.addstr(5+optioncount,4, "%d - %s" % (optioncount+1, lastoption), textstyle)
      except curses.error:
        pass
      screen.refresh()
      # finished updating screen


    x = screen.getch() # Gets user input

    # 'q' character pressed to go to end of list.
    if x == ord('q'): 
      pos = optioncount

    # exit when 2 "x"es are typed
    if x == ord('x'):  # 'x' 
      y = screen.getch() # Gets user input
      if y == ord('x'):
        curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
#        see_json()
#        load_menu(menu_data)
        exit(0)
    if x == ord('/'):  # '/' 
      pos = internal_cmd('process_search', menu['options'])
#swong
      x = ord('x')
      redraw_screen(menu, parent, optioncount, lastoption)
 #     return pos

    # What is user input?
#    if x >= ord('1') and (optioncount < 9 and x <= ord(str(optioncount+1))):
    if x >= ord('1') and (optioncount < 10 and x <= ord(str('9'))):
      pos = x - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
    elif x == 258: # down arrow
      if pos < optioncount:
        pos += 1
      else: pos = 0
    elif x == 259: # up arrow
      if pos > 0:
        pos += -1
      else: pos = optioncount



  # return index of the selected item
  return pos

def get_input (msg):
  _get_input = ''
  try:
    _get_input = raw_input
  except NameError:
    _get_input = input
    pass
  cmd = _get_input(msg)
  return (cmd)


def internal_cmd (cmd, data = object): 
  curses.def_prog_mode()    # save curent curses environment
  os.system('reset')
  screen.clear() #clears previous screen
  screen.refresh() #clears previous screen
  print ("running " + cmd + "\n")

  if cmd == 'help':
    process.process_help()
    ret = get_input("\n<enter to continue> ")
  elif cmd == 'show_config':
    config.see_json()
    config.load_menu(menu_data,1)
    ret = get_input("\n<enter to continue> ")

  elif cmd == 'process_search':
    ret =  process.process_search(data)

  screen.clear() #clears previous screen on key press and updates display based on pos
  curses.reset_prog_mode()   # reset to 'current' curses environment
  curses.curs_set(1)         # reset doesn't do this right
  curses.curs_set(0)
  os.system('amixer cset numid=3 2') # Sets audio output on the pi back to HDMI

  return (ret)
    

# This function calls showmenu and then acts on the selected item
def processmenu(menu, parent=None):
  global debug_line

  optioncount = len(menu['options'])
  exitmenu = False
  while not exitmenu: #Loop until the user exits the menu
    getin = runmenu(menu, parent)
#swong
#    debug_line = "getin = " + str(getin)
    if getin == optioncount:
#    if getin >= optioncount:
        exitmenu = True
#swong
    elif menu['options'][getin]['type'] == INTERNAL:
      internal_cmd(menu['options'][getin]['command'])
    elif menu['options'][getin]['type'] == COMMAND:
      curses.def_prog_mode()    # save curent curses environment
      os.system('reset')
      if menu['options'][getin]['title'] == 'Pianobar':
        os.system('amixer cset numid=3 1') # Sets audio output on the pi to 3.5mm headphone jack
      screen.clear() #clears previous screen
      os.system(menu['options'][getin]['command']) # run the command
      screen.clear() #clears previous screen on key press and updates display based on pos
      curses.reset_prog_mode()   # reset to 'current' curses environment
      curses.curs_set(1)         # reset doesn't do this right
      curses.curs_set(0)
      os.system('amixer cset numid=3 2') # Sets audio output on the pi back to HDMI
    elif menu['options'][getin]['type'] == MENU:
          screen.clear() #clears previous screen on key press and updates display based on pos
          processmenu(menu['options'][getin], menu) # display the submenu
          screen.clear() #clears previous screen on key press and updates display based on pos
    elif menu['options'][getin]['type'] == EXITMENU:
          exitmenu = True

def exit_graceful(msg=''):
    curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
    os.system('clear')
#    see_json()
#    load_menu(menu_data)
    print(msg)
    exit(0)


def usage ():
    s = "Usage: " + __file__ + " [-h] [ -f configfile (default:servers.yaml) ]\n"
    s += "  -h : this help\n"
    s += "  -f : config file\n"
    return (s)



def  getopts():
  global configfile
  try:
    opts, args = getopt.getopt(sys.argv[1:],"hvgf:",["help", "version", "config"])
  except getopt.GetoptError:
    exit_graceful(getopt.GetoptError)
  for opt, arg in opts:
    if opt == '-h':
      process.process_help()
      exit (0)
    elif opt in ("-v", "--version"):
      print("version: " + VERSION)
      exit (0)
    elif opt in ("-g"):
      process.process_gen()
      exit (0)
    elif opt in ("-f", "--config"):
      configfile = arg




def main () :
  global process, config, configfile

  process = Process()

  getopts()

  #see_json()
  try:
    config = Config(configfile)
    configfile = config.configfile
   # init_config(configfile)
  except Exception as e:
    print (e)
    exit (0)

  init_screen()

  config.load_menu(menu_data)
  #exit_graceful()

  # Main program
  processmenu(menu_data)
  exit_graceful()
  #curses.endwin() #VITAL! This closes out the menu system and returns you to the bash prompt.
  #os.system('clear')


if __name__ == '__main__':
  main()


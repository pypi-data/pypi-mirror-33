#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BACKWARD compatibility - START
# For backward compatibility print and input statements:
from __future__ import print_function
if hasattr(__builtins__, 'raw_input'):
    input = raw_input
    print ("got new input")
# BACKWARD compatibility - END

#import ipdb
import shutil
import json
import os
import sys
import yaml
import getopt


#URL='http://localhost:2379'
URL='https://etcd.wongsrus.net.au'

keys_cnt = 0
keys = []
top_str = ''
app_str = ''
env_str = ''
node_str = ''
DEBUG=0
DRYRUN=0
SEE_JSON=0

process = ''

class Process:

  data = 0

  def __init__(self, data=0):
    self.data = data

  def debug (self, msg):
      if DEBUG:
        print (msg + "\n" )

  def doOs (self, cmd_args):
      if len(cmd_args) < 1:
        return
      thecmd = ' '.join(cmd_args[1:])
      f = os.popen(thecmd)
  #    print '%s\n' % (f.read())
      print ('{}\n'.format(f.read()))

  def process_search (self,data = ''):

#    ipdb.set_trace()
    print ("process_search()")

#      if sys.version_info[0] >= 3:
#          get_input = input
#      else:
#          get_input = raw_input
    index = 0

    if data:
      try:
          get_input = raw_input
      except NameError:
          get_input = input
          pass
      pat = get_input("\npattern: ")

      found = 0
      i = 0
      for line in data:
        for key, value in line.items():
          if key == 'title':
            if value.find(pat) != -1:
              found = 1
              break
        if found == 1:
          break
        i += 1;

    index = i
    return (index)

  def process_help (self):
      with open(os.path.dirname(__file__) + '/README.txt', 'r') as fin:
  #    with open('README.txt', 'r') as fin:
        data = fin.read()

      data += "\ninteractive commands"
      data += "\n--------------------"
      data += "\n   xx : exit"
      data += "\n   q  : Go to the end of the list"
      data += "\n   /  : search for server/group"
      print (data)
  #      data=fin.read().replace('\n', '')
      return (data)

  def process_gen (self):
    shutil.copy( os.path.dirname(__file__) + '/servers.yaml', './servers.yaml')
    print ("Generated ./servers.yaml  file\n")


def  _getopts():
  global DRYRUN, DEBUG, SEE_JSON
  try:
    opts, args = getopt.getopt(sys.argv[1:],"hdjs",["headless", "dryrun"])
  except getopt.GetoptError:
    usage('Error:')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      process.process_help()
    if opt == '-s':
      process.process_search()
    if opt == '-j':
      SEE_JSON=1
    if opt == '-d':
      DEBUG=1
    if opt == '--dryrun':
      DRYRUN = True



def main ():
  global process

  process = Process()

  _getopts()




if __name__ == '__main__':
  main()


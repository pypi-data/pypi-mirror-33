#!/usr/bin/env python3

import json
import os
import os.path
import sys
import yaml
import getopt


keys_cnt = 0
keys = []
top_str = ''
app_str = ''
env_str = ''
node_str = ''
DEBUG=0
DRYRUN=0
SEE_JSON=0
DEFAULT_CONFIG_FILE='servers.yaml'

class Config():

  configfile=DEFAULT_CONFIG_FILE
  loaded_nodes_dict = object()

  def __init__(self, inconfig=DEFAULT_CONFIG_FILE):
    self.configfile = inconfig
    if not os.path.isfile( self.configfile ):
      if inconfig == DEFAULT_CONFIG_FILE:
        self.get_configfile()
    self.init_config(self.configfile)
    inconfig = self.configfile

  def get_configfile(self):

    thefile = os.environ['HOME'] + '/.sshplaces/servers.yaml' 
    if os.path.isfile( thefile ):
        self.configfile = thefile
        return
    thefile = '/etc/sshplaces/servers.yaml'
    if os.path.isfile( thefile ):
      self.configfile = thefile
    

  def init_config (self, inconfigfile=DEFAULT_CONFIG_FILE): 
#   global loaded_nodes_dict, configfile

    self.configfile = inconfigfile

    self.debug ("Config.init_config() configfile: " + self.configfile)
    try:
      self.loaded_nodes_dict = yaml.load(open(self.configfile))
    except Exception as e:
      raise Exception(e)
    return (True)


  def debug (self,msg):
      if DEBUG:
        print (msg + "\n" )

  def doOs (self,cmd_args):
      if len(cmd_args) < 1:
        return
      thecmd = ' '.join(cmd_args[1:])
      f = os.popen(thecmd)
  #    print '%s\n' % (f.read())
      print ('{}\n'.format(f.read()))

  def usage (self):
      print ("-h : this help")
      print ("-d : set debug")
      print ("-j : see nodes in json format")
      print ("-n : show loaded nodes from yaml file")
      print ("--dryrun : no change, just dryrun")

  def  getopts(self):
    global DRYRUN, DEBUG, SEE_JSON
    try:
      opts, args = getopt.getopt(sys.argv[1:],"hdj",["headless", "dryrun"])
    except getopt.GetoptError:
      self.usage('Error:')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
        self.usage()
        exit(0)
      if opt == '-j':
        SEE_JSON=1
      if opt == '-d':
        DEBUG=1
      if opt == '--dryrun':
        DRYRUN = True


  def see_json (self):
    with open(self.configfile , 'r') as stream:
      try:
        print(yaml.load(stream))
      except yaml.YAMLError as exc:
        print(exc)


  def build_keys (self, key,val):
    global keys_cnt, keys
  #  keys[keys_cnt]['key'] = key
    keys.append( { "key":key, "val":val })
  #  keys[keys_cnt]['val'] = val
    keys_cnt += 1

  def load_menu (self, menu, dryrun=0):
#   global menu_data
    server_list = []
    print ("\n")
    for groups in self.loaded_nodes_dict:
      for group, serverlist in groups.items():
          print (group)
          servers_list = []
          for servers in serverlist:
              for server, details in servers.items():
                  print ("  {}".format( server))
                  for key, val in details.items():
  #                    print "    " + key + ": " + val
                      print ("    {}: {}".format( key , val))
                      if key == 'cmd':
                         cmd = val
                  servers_list.append( { 'title': server, 'type': 'command', 'command': cmd } )
          if dryrun == 0:
            menu['options'].append ( { 'title': group, 'type': 'menu', 'subtitle': "Select host ", 'options': servers_list } )
                  

  #  menu['options'].append ( { 'title': "group B", 'type': "menu", 'subtitle': "Select host ", 
  #                        'options': [ {'title': "xxx-lap", 'type': 'command', 'command': 'ssh wong-lap.home' }, ] } )


def main ():

  config = Config()

  config.getopts()

  menu_data = {
    'title': "ssh places", 'type': 'menu', 'subtitle': "Please select below ..",
    'options':[
          { 'title': "show configured servers", 'type': "command", 'command': 'config.py' },
    ]
  }

  if SEE_JSON:
    config.see_json()

  config.load_menu(menu_data)
#  print "\nAdding: "


if __name__ == '__main__':
  main()


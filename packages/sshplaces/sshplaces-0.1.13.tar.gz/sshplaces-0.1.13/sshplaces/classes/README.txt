A simple python menu program to help manage ssh to places you want to be.
Built on the curses menu work from:

     https://gist.github.com/abishur/2482046
     http://blog.skeltonnetworks.com/2010/03/python-curses-custom-menu/

Author: Steven hk Wong

Usage: sshplaces.py [-h] [-v] [-g] [-f configuration_file]

  -h this help
  -v version
  -g generates a sample servers.yaml file
  -f configuration file

  if configuration file is unspecified these are the search location in priority:
    ./servers.yaml
    ~/.sshplaces/servers.yaml 
    /etc/sshplaces/servers.yaml 


<pre>

Example configuration file:
============================================================================
  ---
  - home:
      - bedroom-server:
          cmd:   ssh bedroom.example
          state:  active
      - laptop:
          cmd:   ssh laptop.example
          state:  active
  - office:
      - server1:
          cmd:   ssh server1.example
          state:  active
      - server2:
          cmd:   ssh server2.example
          state:  active
  - admin:
      - internet modem (number 1):
          cmd:   ssh -p 2222 admin@modem.example
          state:  active
      - dmz (number 2):
          cmd:   ssh -p 2222 admin@dmz.example
          state:  active

</pre>

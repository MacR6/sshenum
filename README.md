# sshenum
sshenum is a tool that will take a username and an IP/Host and attempt to log in and see if the user can sudo to root by trying to 'sudo id'.  It will also attempt to download the /etc/passwd and /etc/shadow file to a folder named "sshenum" if you tell it to.

This script was written out of necessity during a pen test.  You can give sshenum a single target or a list of hosts to attempt access.  The tool is similar to Hydra for ssh with the additional file grabs.  

Private keys are supported if you have "found" them during a test.

### Requirements
Python 2.7
Paramiko module if you're not using Kali

### Usage
 -h, --help            show this help message and exit
 
  -u USER, --user USER  Username to test
  
  -i HOST, --host HOST  Input single IP/Hostname or use -H/--host_file for
                        multiple IPs

  -P PORT, --port PORT  Leave blank for default ssh port

  -p PASSWORD, --password PASSWORD
                        Input user's password or leave blank and enter on
                        command line

  -H HOST_FILE, --host_file HOST_FILE
                        List of IPs, each on a new line.

  -k PRIVATE_KEY_FILE, --private_key_file PRIVATE_KEY_FILE
                        Input absolute path to private keys

  -f, --files           Grab /etc/passwd and /etc/shadow


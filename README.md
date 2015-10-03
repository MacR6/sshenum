# sshenum
sshenum is a tool that will take a username and an IP/Host and attempt to log in and see if the user has sudo rights by trying to 'sudo id'.  It will also attempt to download the /etc/passwd and /etc/shadow file if you tell it to.

This script was written out of necessity during a pen test.  You can give sshenum a single target or a list of hosts to attempt access.  The tool is similar to Hydra with the additional file grabs.  

Private keys are supported if you have "found" them during a test.

### Requirements
Python 2.7
Paramiko module if you're not using Kali

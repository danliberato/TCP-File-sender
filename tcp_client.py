#Author: Daniel Liberato
#TCP client side
#Requirements: 
# - create paths	./files/
#					./files/rcv/
# - port 8888
import socket 
import sys
import json
import os
import time

max_buffer_size = 5120
host = "localhost"
#host = '' #AWS Public IP
port = 8888
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def Main(): 
	
	try:
		soc.connect((host, port))
	except Exception as err:
		print("Connection error: ", err)
		sys.exit()
		
	print('[ Options ]')
	options()

	opt = ''
	while opt != 'x':
		opt = input('>')
		if opt == 's': 					# SEND FILE TO SERVER
			soc.send(opt.encode())		#send option to server
			nome = input('Select the file: '+os.getcwd()+'/')

			if os.path.exists(nome):
				time.sleep(1)
				soc.send(nome.encode())	#send file name to server
				time.sleep(1)
			
				f_size = os.path.getsize(os.getcwd()+'/'+nome)
				soc.send(str(f_size).encode())	#send file size to server
				
				f = open(nome,'rb')
				data = ''
				print('Transfer initiated...')
				t_start = time.time()
				data = f.read(max_buffer_size)
				while (data):
				   soc.send(data)
				   data = f.read(max_buffer_size)
				f.close()
				t_stop = time.time()
				
				print('File transfer complete in',round(t_stop - t_start,2),'s')
			else:
				print('File not found.')

		elif opt == 'r':				# RECEIVE FILE FROM SERVER
			soc.send(opt.encode())		#send option to server
			f_name = input('File name to receive: ')
	
			soc.send(f_name.encode())
			time.sleep(1)
			response = soc.recv(2).decode()
			if response == '!f':
				
				f_size = int(soc.recv(max_buffer_size).decode())
				
				with open(('files/rcv/'+f_name), 'wb') as f:
					while f_size > 0:
						data_buff = soc.recv(max_buffer_size)
						f_size -= len(data_buff)
						f.write(data_buff)
					
				print('File transfer complete!')
				f.close()
			else:
				print('File not found!')
		else:				#default
			print('Please select an option...')
			options()
	
	soc.send(opt.encode())
	soc.close()
	sys.exit()

def options():
	print('  s : Send a file')
	print('  r : Receive a file')
	print('  x : Exit')

if __name__ == '__main__': 
	Main()

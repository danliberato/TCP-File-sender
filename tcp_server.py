#Author: Daniel Liberato
#TCP server side
#Requirements: 
# - create paths	./files/
#					./files/rcv/
# - port 8888
import socket 
from threading import Thread
import threading 
import os
import sys
import json
import time

option = ''
address = {}
print_lock = threading.Lock()
max_buffer_size = 5120

# thread client
def clientThread(connection, ip, port):
	
	while True:
		rcv_in = connection.recv(max_buffer_size).decode()
		if (not rcv_in) or (rcv_in == 'x'): #		QUIT
			connection.close()
			print("Connection " + ip + ":" + port + " closed!")
			break
		elif rcv_in == 's':
			
			f_name = connection.recv(max_buffer_size).decode()
			f_size = int(connection.recv(max_buffer_size).decode())
			
			print('Client', ip , ':' , port , 'wants to send a file [',f_size,'bytes]...')
			
			with open(('files/'+f_name), 'wb') as f: 
				while f_size > 0:
					data_buff = connection.recv(max_buffer_size)
					f_size -= len(data_buff)
					f.write(data_buff)
					
			print('File transfer complete!')
			f.close()
			
		elif rcv_in == 'r':
			print('Client wants to receive a file.')
			nome = connection.recv(max_buffer_size)
			
			try:
				f = open(os.getcwd()+'/files/'+nome, 'rb')
				text = '!f'
				connection.send(text.encode())
				
				f_size = os.path.getsize(os.getcwd()+'/files/'+nome)
				connection.send(str(f_size).encode())
				time.sleep(1)

				print('Transfer initiated...')
				t_start = time.time()
				data = f.read(max_buffer_size)
				while (data):
				   connection.send(data)
				   data = f.read(max_buffer_size)
				f.close()
				t_stop = time.time()

				f.close()
				print('File transfer complete in',round(t_stop - t_start,2),'s')
			except FileNotFoundError:
				print('File not found!')
				text = '!n'
				connection.send(text.encode())
		else:
			print('Wrong Option: ',rcv_in)
			

#	MAIN
def Main(): 
	host = "localhost"
	#host = ''	# AWS private ip
	port = 8888         # arbitrary non-privileged port
	
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # tells the kernel to reuse a local socket in TIME_WAIT state, without waiting for its natural timeout to expire
	print("Socket created at ", host, ':', port)

	try:
		soc.bind((host, port))
	except:
		print("Bind failed. Error : " + str(sys.exc_info()))
		sys.exit()

	soc.listen(5)       # queue up to 5 requests
	print("Socket now listening")

	while True: # loop to accept client connections
		connection, address = soc.accept()
		ip, port = str(address[0]), str(address[1])
		print("Connected with " + ip + ":" + port)

		try:
			Thread(target=clientThread, args=(connection, ip, port)).start()
		except:
			print("Thread did not start.")
			traceback.print_exc()


if __name__ == '__main__': 
	Main() 

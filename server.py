import socket
import os
import logging
import threading
import sys




def run_server():
	print 'Server started: Ctrl-C to Kill.'
	check = True
	try:
		while check:
			client, addr = server.accept()
			client.settimeout(None)
			print 'Got a connection!'
			
			#ADD OTHER STUFF
			data = 'add cylinder'
			client.send(data.encode())
			reply = client.recv(1024)
			if reply == 'no':
				print 'The user typed no'
				check = False
			else:
				print 'The user typed yes'

	except KeyboardInterrupt:
		print 'Interrupted!'



if __name__ == '__main__':
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	port = 1234
	address = ('', port)
	server.bind(address)
	server.listen(1)

	run_server()
	server.close()



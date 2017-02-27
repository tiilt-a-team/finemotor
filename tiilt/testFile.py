import socket
import bpy

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = '127.0.0.1'
port = 1234
address = (ip, port)

client.connect(address)

data = client.recv(1024).decode()

if (data == 'add cube'):
	bpy.ops.mesh.primitive_cube_add()
	message = 'Cube added'
	client.sendto(message.encode('utf-8'), address)
	print('Cube added')
else:
	message = 'Cube  not added'
	client.sendto(message.encode('utf-8'), address)
	print ('NOOOO!!')







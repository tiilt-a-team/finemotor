import socket, time

HOST = ''
PORT = 8220
ADDR = (HOST,PORT)
BUFSIZE = 2048
data = "(200, 430) 12:23:60 EST -"

bytes = data

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

total_size_sent = len(data)
while(True):
    print(str(total_size_sent) + "   # of messages: " + str(total_size_sent / len(data)))
    client.send(bytes)
    total_size_sent += len(data)
    time.sleep(0.01)




client.close()

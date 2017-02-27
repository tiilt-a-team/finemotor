import json
import socket
import threading
import logging
import time


clients = []


_lock = threading.Lock()

def send_command(name, data = {}):

	global clients

	with _lock:
		data['__cmd__'] = name
		
		jdata = json.dumps(data) + '\n'

		for c in clients:
			try:
				c.send(jdata)
			except socket.timeout as e:
				logging.exception(e)
				continue
			except IOError as e:
				logging.exception(e)
				clients.remove(c)

			time.sleep(0.02)


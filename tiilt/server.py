import socket
import os
import logging
import threading
import sys

import communication as com
from commands import interpret_command



def run_server():
	print 'Server started: Ctrl-C to Kill.'
	try:
		while True:
			pipe, _ = sock.accept()
			pipe.settimeout(0.05)
			com.clients.append(pipe)
	except KeyboardInterrupt:
		print 'Interrupted!'


def cleanup_server():
	sock.close()
	for pipe in com.clients:
		pipe.close()

if __name__ == '__main__':
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('',1234))
	sock.listen(0)
	
	if '-i' in sys.argv or '--interactive' in sys.argv:
		t = threading.Thread(target = run_server)
		t.daemon = True
		try:
			t.start()
			try:
				exit_cmd = 'exit'
				print 'Kill server and exit with "%s"' % exit_cmd
				while True:
					cmd = raw_input('(type) : ').strip().lower()
					if not cmd:
						pass
					elif cmd == exit_cmd:
						break

					if not interpret_command(cmd):
						print 'Unrecognized command "%s"' % cmd
			except EOFError:
				print 'EOF'
			except KeyboardInterrupt:
				pass
		except Exception as e:
			logging.exception(e)
		finally:
			cleanup_server()

	else:
		run_server()
		cleanup_server()



import json
import socket
import threading
import logging
import time
import logging
import Interpreter as Inter
from pprint import pformat

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

_lock = threading.Lock()

debug = True

# connection sockets for clients
clients = []


def send_command(name, data={}):
    """
    Send a command: name is the target function's name, data is the target
    function's kwargs.
    """
    global clients
    with _lock:
        data['__fnc__'] = name
        if debug:
            logging.debug('Sending:', pformat(data))
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


def interpret_command(phrase):
    parsed = Inter.parse_phrase(phrase)
    if parsed is None:
        return False
    for cmd in parsed:
        send_command(cmd[0])
    return True

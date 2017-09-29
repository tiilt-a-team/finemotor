import json
import socket
import threading
import logging
import time
import logging
import Interpreter as Inter
from pprint import pformat
import pickle
from nltk.corpus import wordnet as wn

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

_lock = threading.Lock()

debug = True

# connection sockets for clients
clients = []
commands = ['add', 'move', 'rename', 'view', 'quit', 'select', 'clear', 'undo','redo', 'delete']

def get_synonyms_dict(commands):
    synonyms_dict = {}

    for word in commands:
        synonyms_dict[word] = word

    for comm in commands:
        comm_synonyms = wn.synsets(comm, pos = wn.VERB)
        for word in comm_synonyms:
            for lemma in word.lemmas():
                if (not (lemma.name() in synonyms_dict)):
                    synonyms_dict[lemma.name()]  = comm


    return synonyms_dict


synonyms = get_synonyms_dict(commands)

def send_command(name, eye_info, data={}):
    """
    Send a command: name is the target function's name, data is the target
    function's kwargs.
    """
    global clients
    with _lock:
        data = pickle.dumps(eye_info)
        if debug:
            logging.debug('Sending:' + pformat(data))
        jdata = json.dumps(data) + '\n'
        for c in clients:
            try:
                c.send(data)
            except socket.timeout as e:
                logging.exception(e)
                continue
            except IOError as e:
                logging.exception(e)
                clients.remove(c)
        time.sleep(0.02)


def interpret_command(phrase, eye_data):
    parsed = Inter.parse_phrase(phrase)
    if parsed['verb'] in synonyms:
        parsed['verb'] = synonyms[parsed['verb']]
    print parsed
    if parsed is None:
        return False
    else:
        logging.debug(parsed)
    try:
        parsed['coord'] = eye_data.get()
        send_command(parsed['verb'], parsed)
        return True
    except TypeError:
        return False

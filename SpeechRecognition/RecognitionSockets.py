from __future__ import print_function
import threading
import logging
import socket
import sys
import SpeechToText as Spt
import SocketCommunication as Comm

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

global_phrase = ''


def run_server():
    print('Server started: Ctrl-C to kill')
    try:
        while True:
            pipe, _ = sock.accept()
            pipe.settimeout(0.05)
            Comm.clients.append(pipe)
            print(Comm.clients)
    except KeyboardInterrupt:
        print('interrupted')


def cleanup_server():
    sock.close()
    for pipe in Comm.clients:
        pipe.close()


def run_int(event, phrase_lock):
    """Interpreter thread worker function"""
    logging.debug('Starting Imports')
    import Interpreter as Int
    global global_phrase
    logging.debug('Finished Imports')
    local_phrase = ''
    while True:
        while not event.isSet():
            event.wait(2)
        with phrase_lock:
            logging.debug('Event set')
            local_phrase = global_phrase
            event.clear()
        Int.parse_phrase(local_phrase)


def run_spt(event, phrase_lock):
    """SpeechToTex thread worker function"""
    logging.debug('Starting Imports')
    import SpeechToText as Spt
    global global_phrase
    logging.debug('Finished Imports')
    sd = Spt.SpeechDetector()
    sd.setup_mic()
    local_phrase = ''
    while True:
        local_phrase = sd.run()
        if event.isSet():
            logging.debug('Event already set')
        else:
            with phrase_lock:
                logging.debug('Setting event')
                event.set()
                global_phrase = local_phrase


if __name__ == '__main__':
    HOST = ''   # Symbolic name, meaning all available interfaces
    PORT = 8888 # Arbitrary non-privileged port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    print('Socket created')
    try:
        sock.bind((HOST, PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    print('Socket bind complete')

    #Start listening on socket
    sock.listen(0)
    print('Socket now listening')

    sd = Spt.SpeechDetector()
    sd.setup_mic()

    t = threading.Thread(target=run_server)
    t.daemon = True
    try:
        t.start()
        try:
            exit_cmd = 'exit'
            print('Kill server and exit with "%s"' % exit_cmd)
            while True:
                cmd = sd.run()
                if not cmd:
                    pass
                elif cmd == exit_cmd:
                    break
                if not Comm.interpret_command(cmd):
                        print('bad unrecognized command "%s"' % cmd)
        except EOFError:
            print('EOF')
        except KeyboardInterrupt:
            pass
    except Exception as e:
        logging.exception(e)
    finally:
        cleanup_server()

    sock.close()
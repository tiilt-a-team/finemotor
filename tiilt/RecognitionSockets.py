from __future__ import print_function
import threading
import logging
import socket
import time
import sys
import SpeechToText as Spt
import SocketCommunication as Comm
import Queue

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

global_phrase = ''


def run_server():
    logging.info('Server started: Ctrl-C to kill')
    try:
        while True:
            pipe, _ = sock.accept()
            pipe.settimeout(0.05)
            Comm.clients.append(pipe)
            logging.debug(Comm.clients)
    except KeyboardInterrupt:
        logging.exception('interrupted')


def cleanup_server():
    eye_sock.close()
    sock.close()
    for pipe in Comm.clients:
        pipe.close()


def eye_tracker(lock, event):
    logging.debug('In eye_tracker threading function.')
    global EYE_DATA
    conn, address = eye_sock.accept()
    too_big = False
    while True:
        try:
            chunk = conn.recv(2048).decode()
            if chunk:
                #conn.send("received")
                dechunked = chunk.split("-")
                if not too_big:
                    for seg in dechunked:
                        EYE_DATA.put(seg)
                        if EYE_DATA.full():
                            EYE_DATA.get()
                            too_big = True
                else:
                    for seg in dechunked:
                        EYE_DATA.put(seg)
                        EYE_DATA.get()
            if len(chunk) > 100:
                logging.debug(len(chunk))
        except:
            logging.debug(sys.exc_info()[0])

if __name__ == '__main__':
    HOST = ''   # Symbolic name, meaning all available interfaces
    PORT = 1234 # Arbitrary non-privileged port
    EYE_PORT = 8220
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    logging.debug('Socket created')
    try:
        sock.bind((HOST, PORT))
    except socket.error as msg:
        logging.exception('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    logging.debug('Socket bind complete')

    # Start listening on socket
    sock.listen(0)
    logging.debug('Socket now listening')

    eye_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    eye_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    logging.debug('Socket created')
    try:
        eye_sock.bind((HOST, EYE_PORT))
    except socket.error as msg:
        logging.exception('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    logging.debug('Socket bind complete')

    # Start listening on socket
    eye_sock.listen(0)
    logging.debug('Socket now listening')

    sd = Spt.SpeechDetector()
    #sd.setup_mic()

    t = threading.Thread(target=run_server)
    t.daemon = True

    eye_lock = threading.Lock()
    eye_event = threading.Event()
    eye_thread = threading.Thread(name='eye_tracking', target=eye_tracker, args = (eye_lock, eye_event,))
    eye_thread.daemon = True

    EYE_DATA = Queue.Queue(500)

    try:
        t.start()
        eye_thread.start()
        try:
            exit_cmd = 'exit'
            logging.info('Kill server and exit with "%s"' % exit_cmd)
            while True:
                # FOR TESTING
                cmd = raw_input('Type A Command ').strip().lower()
                # FOR RUNNING
                #cmd = sd.run()

                #eye_event.set()
                if not cmd:
                    pass
                elif cmd == exit_cmd:
                    break
                if not Comm.interpret_command(cmd, EYE_DATA):
                    logging.exception('bad unrecognized command "%s"' % cmd)
                #with eye_lock:
                #    logging.debug(EYE_DATA)
                #    if not Comm.interpret_command(cmd, EYE_DATA):
                #            logging.exception('bad unrecognized command "%s"' % cmd)
                #    EYE_DATA = []
        except EOFError:
            logging.exception('EOF')
        except KeyboardInterrupt:
            pass
    except Exception as e:
        logging.exception(e)
    finally:
        cleanup_server()

    sock.close()
    eye_sock.close()

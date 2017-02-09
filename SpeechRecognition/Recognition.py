import threading
import logging
import time

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


def run_int():
    """Interpreter thread worker function"""
    logging.debug('Starting Imports')
    import Interpreter as Int
    logging.debug('Finished Imports')


def run_spt():
    """SpeechToTex thread worker function"""
    logging.debug('Starting Imports')
    import SpeechToText as Spt
    logging.debug('Finished Imports')
    sd = Spt.SpeechDetector()
    sd.run()

if __name__ == '__main__':
    threads = []

    int_thread = threading.Thread(name='interpreter_thread', target=run_int)
    int_thread.setDaemon(True)
    spt_thread = threading.Thread(name='speech_thread', target=run_spt)

    threads.append(spt_thread)
    threads.append(int_thread)

    for t in threads:
        t.start()

    int_thread.join(30)

    if int_thread.isAlive():
        logging.debug('Import Failed.')
        exit()


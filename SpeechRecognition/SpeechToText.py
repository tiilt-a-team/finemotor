from __future__ import print_function

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

import os
import pyaudio
import wave
import audioop
from collections import deque
import time
import math

"""
Written by Aaron Karp, 2017
Adapted from Sophie Li, 2016
http://blog.justsophie.com/python-speech-to-text-with-pocketsphinx/
"""


class SpeechDetector:
    def __init__(self):
        # Microphone stream config.
        self.CHUNK = 1024  # CHUNKS of bytes to read each time from mic
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000

        self.SILENCE_LIMIT = 2  # Silence limit in seconds. The max ammount of seconds where
        # only silence is recorded. When this time passes the
        # recording finishes and the file is decoded

        self.PREV_AUDIO = 0.8  # Previous audio (in seconds) to prepend. When noise
        # is detected, how much of previously recorded audio is
        # prepended. This helps to prevent chopping the beginning
        # of the phrase.

        self.THRESHOLD = 4500
        self.num_phrases = -1

        MODELDIR = "libraries/pocketsphinx/model"
        # DATADIR = "libraries/pocketsphinx/test/data"

        # Create a decoder with certain model
        config = Decoder.default_config()
        # turn off pocketsphinx output
        config.set_string('-logfn', '/dev/null')
        config.set_string('-hmm', os.path.join(MODELDIR, 'en-us/en-us'))
        config.set_string('-lm', os.path.join(MODELDIR, 'en-us/en-us.lm.bin'))
        config.set_string('-dict', os.path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
        config.set_string('-kws', 'custom_dict_files/sample_keyword_list.txt')

        # Creates decoder object for streaming data.
        self.decoder = Decoder(config)

    def setup_mic(self, num_samples=50):
        """ Gets average audio intensity of your mic sound. You can use it to get
            average intensities while you're talking and/or silent. The average
            is the avg of the .2 of the largest intensities recorded.
        """

        print("Getting intensity values from mic.")
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)

        values = [math.sqrt(abs(audioop.avg(stream.read(self.CHUNK), 4)))
                  for x in range(num_samples)]
        values = sorted(values, reverse=True)
        r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
        print(" Finished ")
        print(" Average audio intensity is ", r)
        stream.close()
        p.terminate()

        if r < 3000:
            # self.THRESHOLD = 3500
            self.THRESHOLD = min(r * 3 / 2, 3500)  # Good for Yeti mic in quiet room
        else:
            self.THRESHOLD = r + 100

    def save_speech(self, data, p):
        """
        Saves mic data to temporary WAV file. Returns filename of saved
        file
        """
        filename = 'tempfiles/output_' + str(int(time.time()))
        # writes data to WAV file
        data = ''.join(data)
        wf = wave.open(filename + '.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.RATE)  # TODO make this value a function parameter?
        wf.writeframes(data)
        wf.close()
        return filename + '.wav'

    def decode_phrase(self, wav_file):
        self.decoder.start_utt()
        stream = open(wav_file, "rb")
        while True:
            buf = stream.read(1024)
            if buf:
                self.decoder.process_raw(buf, False, False)
            else:
                break
        self.decoder.end_utt()
        words = []
        # [words.append(seg.word) for seg in self.decoder.seg()]
        hypothesis = self.decoder.hyp()
        for best, i in zip(self.decoder.nbest(), range(10)):
            words.append(best.hypstr + ' -- model score: ' + str(best.score))
        return words

    def check_phrase(self, words):
        idx_to_get = 0  # words.index("zig")
        command = words[0]
        print("Top Model: ", command)
        print()
        known_words = []
        unknown_words = []
        for i in range(len(command)):
            curr = command[i]
            if "<" in curr:
                unknown_words.append(curr)
            elif "[" in curr:
                unknown_words.append(curr)
            else:
                known_words.append(curr)
        # print "Known words: ", known_words
        # print "Unknown words: ", unknown_words
        best_phrase = ''.join(known_words)
        best_score = best_phrase.split(' ')[-1:]
        return ' '.join(best_phrase.split(' ')[:-4])

    def run(self):
        """
        Listens to Microphone, extracts phrases from it and calls pocketsphinx
        to decode the sound
        """

        # Open stream
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        print("* Mic set up and listening. ")

        audio2send = []
        cur_data = ''  # current chunk of audio data
        rel = self.RATE / self.CHUNK
        slid_win = deque(maxlen=self.SILENCE_LIMIT * rel)
        # Prepend audio from 0.5 seconds before noise was detected
        prev_audio = deque(maxlen=self.PREV_AUDIO * rel)
        started = False

        while True:
            cur_data = stream.read(self.CHUNK)
            slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))

            if sum([x > self.THRESHOLD for x in slid_win]) > 0:
                if not started:
                    print("Starting recording of phrase")
                    started = True
                audio2send.append(cur_data)

            elif started:
                print("Finished recording, decoding phrase")
                filename = self.save_speech(list(prev_audio) + audio2send, p)
                r = self.decode_phrase(filename)
                print()
                print("TOP 10 DETECTED: ", r)
                print()

                best_phrase = self.check_phrase(r)
                #############################################################################################################################
                # Inter.parse_phrase(best_phrase)
                #############################################################################################################################
                # Removes temp audio file
                os.remove(filename)
                stream.close()
                # Reset all
                print("Ending Loop")
                return best_phrase

            else:
                prev_audio.append(cur_data)

        print("* Done listening")
        stream.close()
        p.terminate()


if __name__ == "__main__":
    sd = SpeechDetector()
    sd.run()

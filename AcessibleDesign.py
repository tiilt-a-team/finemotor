import os
import signal
import subprocess
import time
import sys
import platform
from Tkinter import *
import tkFileDialog

global subs
global directory

def main():
	global subs
	global directory

	subs = []
	directory = None

	sys.stdout.write("\033[1;31m") # Red
	print 'Press Ctrl-C to kill all AccessibleDesign processes'

	plat = platform

	try:
		root = Tk()
		root.withdraw()
		root.update()
		directory = tkFileDialog.askdirectory(initialdir='.')
		while not directory:
			time.sleep(0.1)
		root.update()
		root.destroy()

		if plat.system() == 'Windows': # Windows
			eye_tribe = subprocess.Popen("EyeTracker/EyeTribe.exe", stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
		elif plat.system() == 'Darwin': # MacOS
			eye_tribe = subprocess.Popen("EyeTracker/EyeTribe", stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
		else:
			print 'Unsupported Operating System'
			exit()
		
		subs.append(eye_tribe)
		recognition_sockets = subprocess.Popen(['python', 'RecognitionSockets.py'], cwd='SpeechRecognition', stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
		subs.append(recognition_sockets)

		print directory
		blender = subprocess.Popen('./blender.app/Contents/MacOS/blender -d --python tiilt/blender.py', cwd=directory, shell=True, preexec_fn=os.setsid)
		subs.append(blender)

		sys.stdout.write("\033[0;32m") # Green
		print ''
		print 'Process PIDs...'
		print 'eye_tribe = ', eye_tribe.pid
		print 'recognition_sockets = ', recognition_sockets.pid
		print 'blender = ', blender.pid
		sys.stdout.write("\033[0;0m") # Reset
		print ''

	except Exception as e:
		# If any of them couldn't open
		raise e
		exit()

	while True:
		try:
			for sub in subs:
				if sub.poll():
					exit()
		except KeyboardInterrupt:
			exit()


def openDir():
    global directory
    directory = tkFileDialog.askdirectory(initialdir='.')

# Kill processes and exit shell
def exit():
	global subs
	sys.stdout.write("\033[1;31m") # Red
	for sub in subs:
		try:
			os.killpg(os.getpgid(sub.pid), signal.SIGTERM)
		except Exception as e:
			print ''
			print 'Subprocess error'
			print e, ' -- ', sub.pid
	sys.stdout.write("\033[0;0m") # Reset
	print ''
	sys.exit()




main()
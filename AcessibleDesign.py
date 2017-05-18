import os
import signal
import subprocess
import time
import sys
import platform

global subs

def main():
	global subs
	subs = []

	sys.stdout.write("\033[1;31m") # Red
	print 'Press Ctrl-C to kill all AccessibleDesign processes'

	plat = platform

	try:
		if plat.system() == 'Windows': # Windows
			eye_tribe = subprocess.Popen("EyeTracker/EyeTribe.exe", stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
		elif plat.system() == 'Darwin': # MacOS
			eye_tribe = subprocess.Popen("EyeTracker/EyeTribe", stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
		else:
			print 'Unsupported Operating System'
			exit()
		subs.append(eye_tribe)
		#time.sleep(1)
		recognition_sockets = subprocess.Popen(['python', 'RecognitionSockets.py'], cwd='SpeechRecognition', stdout=subprocess.PIPE, shell=False, preexec_fn=os.setsid)
		subs.append(recognition_sockets)
		#time.sleep(1)

		sys.stdout.write("\033[0;32m") # Green
		print ''
		print 'Process PIDs...'
		print 'eye_tribe = ', eye_tribe.pid
		print 'recognition_sockets = ', recognition_sockets.pid
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
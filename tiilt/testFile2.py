from communication import send_command



def testFunction():
	command = input('Please enter the command to send: ')
	send_command(command)

testFunction()

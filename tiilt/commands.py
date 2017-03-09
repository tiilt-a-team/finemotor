import logging
from functools import partial
from communication import send_command

def view_from(direction):
	logging.debug('Viewing from %s' %direction)
	send_command('view_%s' % direction)

def move_object(object_name):
	pass

_mode_mapping = {
	'object' : 'object',
	'pottery' : 'sculpt',
}

def enter_mode(mode):
	mode_command = mode_mapping[mode]

	if mode_command:
		send_command('mode_%s' % mode_command)


_cmd_mapping = {
	'above' : partial(view_from, 'top'),
	'left' : partial(view_from, 'left'),
	'right' : partial(view_from, 'right'),
	'below' : partial(view_from, 'bottom'),
	'clear' : partial(send_command, 'clear_everything'),
	'undo' : partial(send_command, 'undo'),
	'move' : partial(send_command, 'move'),
	'add' : partial(send_command, 'add'),
}

def interpret_command(cmd):
	cmd_name = cmd.split(' ')[0]
	print ('You entered '+cmd_name+' as the command.')
	if cmd_name not in _cmd_mapping:
		logging.debug('Unrecogniezed command %s' %cmd)
		return False
	'''
	strArgs = [1,2,3]
	for i in range(3):
		print i
		strArgs[i] = cmd.split(' ')[i]
	'''
	#retval = _cmd_mapping[strArgs[0]]({'shape' : strArgs[1]})
	print cmd_name
	print cmd.split(' ')[1]
	retval = _cmd_mapping[cmd_name]({'shape' : cmd.split(' ')[1]})
	if retval is not None:
		return retval

	return True

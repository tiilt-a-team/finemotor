import logging
from functools import partial
from communication import send_command

def view_from(direction):
	logging.debug('Viewing from %s' %direction)
	send_command('view_%s' % direction)

def add_object(object_name):
	logging.debug('Adding %s' %object_name)
	send_command('add_%s' %object_name)

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
	'add cube' : partial(add_object, 'cube'),
	'add cylinder' : partial(add_object, 'cylinder'),
	'clear' : partial(send_command, 'clear_everything'),
}

def interpret_command(cmd):
	if cmd not in _cmd_mapping:
		logging.debug('Unrecogniezed command %s' %cmd)
		return False

	retval = _cmd_mapping[cmd]()
	if retval is not None:
		return retval

	return True

import logging
from functools import partial
from communication import send_command

def view_from(direction):
	send_command('view_%s' % direction)

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
	'front' : partial(view_from, 'front'),
	'add' : partial(send_command, 'sculpt_add'),
}

def interpret_command(cmd):
	if cmd not in _cmd_mapping:
		return False

	retval = _cmd_mapping[cmd]()
	if retval is not None:
		return retval

	return True

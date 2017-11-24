from random import randint
HIGH = 1
LOW = 0
OUT = 1
IN = 0
BCM = 'bcm'

global STATE


def setmode(mode):
	pass


def setup(pin, type):
	pass


def output(pin, direction):
	global STATE
	STATE = direction


def cleanup(pin):
	pass


def input(pin):
	global STATE
	return STATE

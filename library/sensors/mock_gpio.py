from random import randint
HIGH = 1
LOW = 0
OUT = 1
IN = 0
BCM = 'bcm'


def setmode(mode):
	pass


def setup(pin, type):
	pass


def output(pin, direction):
	pass


def cleanup(pin):
	pass


def input(pin):
	return randint(0, 1)

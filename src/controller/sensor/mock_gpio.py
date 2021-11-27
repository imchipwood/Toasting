from random import randint
HIGH = 1
LOW = 0
OUT = 1
IN = 0
BCM = 'bcm'

global STATE
STATE = dict()


def setmode(mode: str):
	pass


def setup(pin: int, direction: int):
	global STATE
	STATE[pin] = False


def output(pin: int, direction: int):
	global STATE
	STATE[pin] = bool(direction)


def cleanup(pin: int):
	global STATE
	if pin in STATE:
		del STATE[pin]


def input(pin: int) -> bool:
	global STATE
	STATE[pin] = bool(randint(0, 1))
	return STATE[pin]

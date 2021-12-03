from random import randint
HIGH = 1
LOW = 0
OUT = 1
IN = 0
PUD_UP = 22
PUD_DOWN = 21
BCM = 'bcm'

STATES = dict()
DIRECTIONS = dict()


def setmode(mode: str):
	pass


def setup(pin: int, direction: int, pull_up_down: int = PUD_UP):
	global STATES, DIRECTIONS
	DIRECTIONS[pin] = direction
	STATES[pin] = 0 if direction == OUT else int(pull_up_down == PUD_UP)


def output(pin: int, value: int):
	global STATES, DIRECTIONS
	if DIRECTIONS.get(pin) == OUT:
		STATES[pin] = value


def input(pin: int) -> int:
	global STATES, DIRECTIONS
	if DIRECTIONS.get(pin) == OUT:
		STATES[pin] = randint(0, 1)
	return STATES[pin]


def cleanup(pin: int):
	global STATES, DIRECTIONS
	if pin in STATES:
		del STATES[pin]
	if pin in DIRECTIONS:
		del DIRECTIONS[pin]

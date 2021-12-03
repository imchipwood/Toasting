HIGH = 1
LOW = 0
OUT = 0
IN = 1
PUD_UP = 22
PUD_DOWN = 21
PUD_OFF = 20
BCM = 11
BOARD = 10

STATES = dict()
DIRECTIONS = dict()


def setmode(mode: int):
	pass


def setup(pin: int, direction: int, pull_up_down: int = PUD_UP):
	global STATES, DIRECTIONS
	DIRECTIONS[pin] = direction
	STATES[pin] = 0 if direction == OUT else int(pull_up_down == PUD_UP)


def output(pin: int, value: int):
	global STATES
	STATES[pin] = value


def input(pin: int) -> int:
	global STATES, DIRECTIONS
	return STATES[pin]


def cleanup(pin: int):
	global STATES, DIRECTIONS
	if pin in STATES:
		del STATES[pin]
	if pin in DIRECTIONS:
		del DIRECTIONS[pin]

from random import randint
from typing import List


class SpiDev:
	"""
	Mock SpiDev object for running on non-rpi systems
	"""
	def __init__(self):
		super()

		self.max_speed_hz = 0
		self.cshigh = False
		self.bits_per_word = 8
		self.lsbfirst = False
		self.mode = 0

	def open(self, bus, device):
		pass

	def close(self):
		pass

	def xfer(self, bytes: List[int]):
		for x in range(0, len(bytes)):
			bytes[x] = randint(0, 255)
		return bytes

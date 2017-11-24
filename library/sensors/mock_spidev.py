from random import randint


class SpiDev(object):
	def __init__(self):
		super(SpiDev, self).__init__()

		self.max_speed_hz = 0
		self.cshigh = False
		self.bits_per_word = 8
		self.lsbfirst = False
		self.mode = 0

	def open(self, bus, device):
		pass

	def close(self):
		pass

	def xfer(self, bytes):
		# for x in range(0, len(bytes)):
		# 	bytes[x] = randint(0, 255)
		return [0] * len(bytes)



class SpiDev(object):
	def __init__(self):
		super(SpiDev, self).__init__()

		self.max_speed_hz = 0
		self.cshigh = False
		self.bits_per_word = 8
		self.lsbfirst = False
		self.mode = 0

	def open(self, arga, argb):
		pass

	def close(self):
		pass

	def xfer(self, val):
		return [0] * len(val)

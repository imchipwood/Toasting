import logging

from library.other.setupLogging import getLogger

try:
	# RPi
	import spidev
except:
	# Other
	logging.info("Failed to import spidev - using mock spidev libraries")
	import library.sensors.mock_spidev as spidev

VALID_UNITS = ['celcius', 'fahrenheit']


class ExceptionTemplate(Exception):
	def __call__(self, *args):
		return self.__class__(*(self.args + args))

	def __str__(self):
		return ': '.join(self.args)


class TCNoTCError(ExceptionTemplate):
	pass


class TCGndShortError(ExceptionTemplate):
	pass


class TCVccShortError(ExceptionTemplate):
	pass


class TCError(ExceptionTemplate):
	pass


class UnitError(ExceptionTemplate):
	pass


class Thermocouple(object):
	def __init__(self, csPin=0, debugLevel=logging.INFO):
		super(Thermocouple, self).__init__()

		self.logger = getLogger('Thermocouple', debugLevel)

		# Temperature is always stored in celcius
		self._temp = 0.0
		self._refTemp = 0.0

		self.spi = None
		self._csPin = -1

		# Use setter for csPin to set new pin & call init
		self.csPin = csPin

	@property
	def temperature(self):
		return self._temp

	@property
	def refTemperature(self):
		return self._refTemp

	@property
	def csPin(self):
		return self._csPin

	@csPin.setter
	def csPin(self, pin):
		# Check pin is valid
		if pin not in [0, 1]:
			raise Exception("SPI CS pin must be 0 or 1")

		# Is pin different?
		if pin == self.csPin:
			# No, don't need to re-init
			return

		# Pin is valid & new - close existing SPI, set new pin, and initialize new SPI
		self.cleanup()
		self._csPin = pin
		self.init()

	def init(self):
		"""Initialize SPI interface"""
		self.spi = spidev.SpiDev()
		# CPOL = 0 -> clock default low, thus CPHA = 0 -> capture on rising edge
		self.spi.open(self.csPin, 0)
		# set SCLK frequency to 4MHz (MAX31855 has a max of 5MHz)
		self.spi.max_speed_hz = 4000000
		# set CS active low
		self.spi.cshigh = False
		# set MSB first (only way RPi can transfer)
		self.spi.bits_per_word = 8
		# CPOL|CPHA 0b00 = 0, 0b11 = 3
		self.spi.lsbfirst = False
		self.spi.mode = 0

	def read(self):
		"""Perform an SPI read of the MAX31855 Thermocouple

		@return: float temperature in degrees celcius
		"""
		val = [0, 0, 0, 0]
		try:
			val = self.spi.xfer(val)			# get four bytes as an array of four integers
		except:
			self.logger.exception("exception during SPI read")
			raise

		tmpval = ''
		for b in val:
			# store the value in base 16 and strip off the '0b' portion
			h = hex(b)[2:]
			if b < 16:
				# add leading 0s if number is small enough
				h = '0' + h
			tmpval += h
		# convert string from base 16 to base 10
		val = int(tmpval, 16)

		if (val & 0x0001) and (val & 0x10000):
			raise TCNoTCError('no thermocouple attached')
		if (val & 0x0002) and (val & 0x10000):
			raise TCGndShortError('short to ground')
		if (val & 0x0004) and (val & 0x10000):
			raise TCVccShortError('short to vcc')
		if val & 0x20008:
			raise TCError('dummy 0 bits missing')

		# internal MAX31855 temp
		ival = val
		# get rid of fault bits
		ival >>= 4
		# pull off bottom 11 bits
		it = ival & 0x7FF
		# check sign bit and switch sign if necessary
		if ival & 0x800:
			it *= -1.0

		# LSB = 2^(-4) (0.0625 degrees Celcius)
		it *= 0.0625
		self._refTemp = it

		# thermocouple temp
		# shift the bottom 18 bits out, leaving only 14 bit thermocouple data
		val >>= 18
		# pull off bottom 13 bits
		tcelcius = val & 0x3FFF
		# check sign bit and switch sign if necessary
		if val & 0x2000:
			tcelcius |= 0xC000

		# LSB = 2^(-2) (0.25 degrees Celcius)
		tcelcius *= 0.25

		# we got through without exceptions - update temp var
		self._temp = tcelcius
		return self.temperature

	def cleanup(self):
		"""Close SPI interface"""
		try:
			if self.spi:
				self.spi.close()
				self.logger.debug("SPI shut down")
		except Exception as e:
			self.logger.exception("spi.close() exception")

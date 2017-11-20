import logging

from library.other.setupLogging import getLogger
from library.sensors.sensor_relay import Sensor

# import proper GPIO/spidev libraries depending on system
try:
	# RPi
	import RPi.GPIO as GPIO
except:
	# Other
	import library.sensors.MockGPIO as GPIO
try:
	# RPi
	import spidev
except:
	# Other
	import library.sensors.MockSpidev as spidev

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


class Thermocouple(Sensor):
	def __init__(self, spiCsPin, enable=GPIO.LOW, debugLevel=logging.INFO):
		super(Thermocouple, self).__init__(spiCsPin, enable=enable, debugLevel=debugLevel)

		self.logger = getLogger('Thermocouple', debugLevel)

		self._units = 'celcius'

		# Temperature is always stored in fahrenheit
		self._temp = 0.0
		self._lastTemp = self.temperature
		self._refTemp = 0.0

		self.spi = spidev.SpiDev()
		self.init()

	@property
	def csPin(self):
		return self.pin

	@csPin.setter
	def csPin(self, pin):
		super(Thermocouple, self).__init__(pin, self.positive, debugLevel=self.debugLevel)

	@property
	def temperature(self):
		# if self.units == 'celcius':
		return self._temp
		# else:
		# 	return self._temp * 9.0 / 5.0 + 32.0

	@property
	def refTemperature(self):
		# if self.units == 'celcius':
		return self._refTemp
		# else:
		# 	return self._refTemp * 9.0 / 5.0 + 32.0

	@property
	def units(self):
		return self._units

	@units.setter
	def units(self, units):
		if units not in VALID_UNITS:
			raise UnitError('Allowable units are {}'.format(", ".join(VALID_UNITS)))
		self._units = units

	def init(self):
		# setup CS pin
		super(Thermocouple, self).init()

		# Setup SPI
		self.logger.debug("SPI Setup")
		# CPOL = 0 -> clock default low, thus CPHA = 0 -> capture on rising edge
		self.spi.open(0, 0)
		# set SCLK frequency to 4MHz (MAX31855 has a max of 5MHz)
		self.spi.max_speed_hz = 4000000
		# set CS active low and "disable" (set it high)
		self.spi.cshigh = False
		self.disable()
		# set MSB first (only way RPi can transfer)
		self.spi.bits_per_word = 8
		# CPOL|CPHA 0b00 = 0, 0b11 = 3
		self.spi.lsbfirst = False
		self.spi.mode = 0

	def cleanup(self):
		# clean up CS
		super(Thermocouple, self).cleanup()

		try:
			self.spi.close()
			self.logger.debug("SPI shut down")
		except Exception as e:
			self.logger.exception("exception during spi.close()")
			self.logger.exception(e.message)

	def read(self):
		self.logger.debug("tcread")
		self.enable()
		val = [0, 0, 0, 0]
		try:
			self.logger.debug('spi xfer')
			val = self.spi.xfer(val)			# get four bytes as an array of four integers
			self.logger.debug("spi: {}".format(" ".join([str(bin(x)) for x in val])))
		except:
			self.logger.exception("exception during SPI read")
			raise
		finally:
			self.disable()

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

		# we got through without exceptions, set lasttemp to temp read last time
		self._lastTemp = self.temperature
		self._temp = tcelcius
		self.logger.debug("temp: {}".format(self.temperature))
		return self.temperature

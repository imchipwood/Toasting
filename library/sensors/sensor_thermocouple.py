import logging

from library.other.setupLogging import getLogger

try:
	# RPi
	import spidev
except:
	# Other
	print("!!!WARNING!!! Failed to import spidev - using mock spidev library")
	import library.sensors.mock_spidev as spidev


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


class Thermocouple(object):

	VALID_UNITS = ["celsius", "fahrenheit"]
	# RPi has a single SPI bus (0)
	SPI_BUS = 0

	# RPi has two SPI CS pins, set CS active low
	SPI_CS_VALID_PINS = [0, 1]
	SPI_CS_LOGIC_HIGH = False

	# set SCLK frequency to 4MHz (MAX31855 has a max of 5MHz)
	SPI_CLK_FREQ = 4000000
	SPI_BITS_PER_WORD = 8

	# CPOL = 0 -> clock default low, thus CPHA = 0 -> capture on rising edge
	# CPOL|CPHA 0b00 = 0
	SPI_MODE = 0
	# set MSB first (only way RPi can transfer)
	SPI_LSB_FIRST = False

	def __init__(self, csPin=0, units='celsius', debugLevel=logging.INFO):
		super(Thermocouple, self).__init__()

		self.logger = getLogger('Thermocouple', debugLevel)

		self._units = units

		# Temperature is always stored in celsius
		self._temp = 0.0
		self._refTemp = 0.0

		self.spi = None
		self._csPin = -1

		# Use setter for csPin to set new pin & call init
		self.csPin = csPin

	@property
	def temperature(self):
		return self._temp if self.units == 'celsius' else self.ConvertCelsiusToFahrenheit(self._temp)

	@property
	def rawTemperature(self):
		return self._temp

	@property
	def refTemperature(self):
		return self._refTemp if self.units == 'celsius' else self.ConvertCelsiusToFahrenheit(self._refTemp)

	@property
	def rawRefTemperature(self):
		return self._refTemp

	@property
	def units(self):
		return self._units

	@units.setter
	def units(self, units):
		self._units = self.CheckUnits(units)

	@staticmethod
	def CheckUnits(units):
		units = units.lower()
		assert units in Thermocouple.VALID_UNITS
		return units

	@property
	def csPin(self):
		return self._csPin

	@csPin.setter
	def csPin(self, pin):
		# Check pin is valid
		pin = self.CheckSPICSPin(pin)

		# Is pin different?
		if pin == self.csPin:
			# No, don't need to re-init
			return

		# Pin is valid & new - close existing SPI, set new pin, and initialize new SPI
		self.cleanup()
		self._csPin = pin
		self.init()

	@staticmethod
	def CheckSPICSPin(pin):
		"""
		Check SPI CS pin is valid, raise exception if not, return int pin if valid
		@param pin: target pin
		@type pin: str or int
		@rtype: int
		"""
		pin = int(pin)
		msg = "SPI CS pin must be one of the following: {}".format(
			", ".join(str(x) for x in Thermocouple.SPI_CS_VALID_PINS)
		)
		assert pin in Thermocouple.SPI_CS_VALID_PINS, msg
		return pin

	def init(self):
		"""
		Initialize SPI interface
		"""
		self.spi = spidev.SpiDev()
		self.spi.open(bus=self.SPI_BUS, device=self.csPin)
		self.spi.max_speed_hz = self.SPI_CLK_FREQ
		self.spi.cshigh = self.SPI_CS_LOGIC_HIGH
		self.spi.bits_per_word = self.SPI_BITS_PER_WORD

		self.spi.lsbfirst = self.SPI_LSB_FIRST
		self.spi.mode = self.SPI_MODE

	def read(self):
		"""
		Perform an SPI read of the MAX31855 Thermocouple
		@return: Thermocouple temperature in currently configured units
		@rtype: float
		"""
		spiReadBytes = [0, 0, 0, 0]
		try:
			spiReadBytes = self.spi.xfer(spiReadBytes)  # get four bytes as an array of four integers
		except:
			self.logger.exception("exception during SPI read")
			raise

		# Convert the result to an integer
		spiReadResult = self.ByteListToInteger(spiReadBytes)

		# Check the result for errors
		self.CheckSPIReadForErrors(spiReadResult)

		# Calculate reference (internal) temp
		self._refTemp = self.CalculateReferenceTemperature(spiReadResult)

		# Calculate thermocouple temp
		self._temp = self.CalculateThermocoupleTemperature(spiReadResult)

		# Return the value
		return self.temperature

	@staticmethod
	def ConvertCelsiusToFahrenheit(celsius):
		"""
		Convert a temp to the specified units
		@param celsius: Temperature in Celsius
		@type celsius: float
		@return: Converted temperature
		@rtype: float
		"""
		return celsius * 9.0 / 5.0 + 32.0

	@staticmethod
	def CheckSPIReadForErrors(spiReadResult):
		"""
		Raise an exception if any errors are found in the SPI value
		@param spiReadResult: Result of SPI read
		@type spiReadResult: int
		"""
		if spiReadResult & 0x10000:
			if spiReadResult & 0x0001:
				raise TCNoTCError('no thermocouple attached')
			elif spiReadResult & 0x0002:
				raise TCGndShortError('short to ground')
			elif spiReadResult & 0x0004:
				raise TCVccShortError('short to vcc')
		elif spiReadResult & 0x20008:
			raise TCError('dummy 0 bits missing')

	@staticmethod
	def ByteListToInteger(bytes):
		"""
		Sum a list of bytes (integers) and return the integer value
		@param bytes: list of single byte integer values
		@type bytes: list[int]
		@return: converted value
		@rtype: int
		"""
		hexAccumulator = ""
		for byte in bytes:

			# store the value in base 16 and strip off the '0b' portion
			byteInHex = hex(byte)[2:]

			# Pad with 0s
			if len(byteInHex) < 2:
			# if byte < 16:
				byteInHex = "0" + byteInHex

			# Add the new hex to the string
			hexAccumulator += byteInHex

		# Convert string from base 16 to base 10
		return int(hexAccumulator, 16)

	@staticmethod
	def CalculateReferenceTemperature(spiReadResult):
		"""
		Calculate the reference temperature from the SPI read
		@param spiReadResult: Result of SPI read
		@type spiReadResult: int
		@return: Reference temperature in Celsius
		@rtype: float
		"""
		# Get rid of fault bits (shift off bottom byte)
		spiReadResult >>= 4

		# Use only bottom 11 bits
		refTemp = spiReadResult & 0x7FF

		# Check sign bit and switch sign if necessary
		if spiReadResult & 0x800:
			# refTemp *= -1.0
			refTemp = (0x7FF + 1 - refTemp) * -1.0

		# Scale value: LSB = 2^(-4) (0.0625 degrees Celsius)
		return refTemp * 0.0625

	@staticmethod
	def CalculateThermocoupleTemperature(spiReadResult):
		"""
		Given the full SPI read result integer, calculate the temp in celsius
		@param spiReadResult: Result of SPI read
		@type spiReadResult: int
		@return: Thermocouple temperature in Celsius
		@rtype: float
		"""
		# Shift the bottom 18 bits out, leaving only 14 bit thermocouple data
		spiReadResult >>= 18

		# Pull off bottom 13 bits
		tcelsius = spiReadResult & 0x3FFF

		# Check sign bit and switch sign if necessary
		if spiReadResult & 0x2000:
			tcelsius = (0x3FFF + 1 - tcelsius) * -1.0

		# Scale value: LSB = 2^(-2) (0.25 degrees Celsius)
		return tcelsius * 0.25

	def cleanup(self):
		"""
		Close SPI interface
		"""
		try:
			if self.spi:
				self.spi.close()
				self.logger.debug("SPI shut down")
		except:
			self.logger.exception("spi.close() exception")

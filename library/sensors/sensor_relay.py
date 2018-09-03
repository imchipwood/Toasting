import logging

from library.other.setupLogging import getLogger

try:
	# RPi
	import RPi.GPIO as GPIO
except:
	# Other
	logging.info("Failed to import RPi.GPIO - using mock GPIO libraries")
	import library.sensors.mock_gpio as GPIO


class Sensor(object):
	ACTIVE_HIGH = GPIO.HIGH

	def __init__(self, pin, activeHigh=True, debugLevel=logging.INFO):
		"""
		Constructor
		@param pin: GPIO pin number to set up (BCM)
		@type pin: int or str
		@param activeHigh: GPIO pin output direction
		@type activeHigh: bool
		@param debugLevel: logging level
		@type debugLevel: int
		"""
		super(Sensor, self).__init__()

		self.ACTIVE_HIGH = GPIO.HIGH if activeHigh else GPIO.LOW

		self.logger = getLogger('Sensor', debugLevel)
		self.debugLevel = debugLevel
		self._state = False
		self.state = None
		self._pin = None
		self.pin = pin

	@classmethod
	def HIGH(cls):
		"""
		Get the "enabled" output value for this GPIO pin
		@return: GPIO.HIGH or GPIO.LOW
		@rtype: int
		"""
		return cls.ACTIVE_HIGH

	@classmethod
	def LOW(cls):
		"""
		Get the "disabled" output value for this GPIO pin
		@return: GPIO.HIGH or GPIO.LOW
		@rtype: int
		"""
		return GPIO.LOW if cls.ACTIVE_HIGH else GPIO.LOW

	@property
	def state(self):
		"""
		Get current state
		@return: Current state
		@rtype: bool
		"""
		return self._state

	@state.setter
	def state(self, state):
		"""
		Sets new current state
		@param state: New state
		@type state: bool
		"""
		self._state = bool(state)

	@property
	def pin(self):
		"""
		Get current GPIO pin number
		@return: Current GPIO pin number
		@rtype: int
		"""
		return self._pin

	@pin.setter
	def pin(self, pin):
		"""
		Initialize a new pin. Sets up GPIO & enables pin as output. Cleans old pin if necessary
		@param pin: Pin to initialize
		@type pin: str or int
		"""
		pin = int(pin)
		if pin != self.pin:
			self.cleanup()
			self._pin = pin
			self.init()

	def init(self):
		"""
		Initialize GPIO
		"""
		self.logger.debug("initing pin {}".format(self.pin))
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin, GPIO.OUT, initial=self.LOW())
		self.disable()

	def enable(self):
		"""
		"Enable" the output based on the configured active high or low
		"""
		GPIO.output(self.pin, self.HIGH())
		self.state = True

	def disable(self):
		"""
		"Disable" the output based on the configured active high or low
		"""
		GPIO.output(self.pin, self.LOW())
		self.state = False

	def toggle(self):
		"""
		Toggle the relay - i.e. switch states
		"""
		if self.state:
			self.disable()
		else:
			self.enable()

	def cleanup(self):
		"""
		Cleanup all GPIO
		"""
		try:
			GPIO.cleanup(self.pin)
			self.logger.debug("GPIO.cleanup({}) complete".format(self.pin))
		except:
			self.logger.exception("issue during GPIO.cleanup()")


class Relay(Sensor):
	def __init__(self, pin, activeHigh=True, startingState=False, debugLevel=logging.INFO):
		"""
		Constructor
		@param pin: GPIO pin number to set up (BCM)
		@type pin: int or str
		@param activeHigh: GPIO pin output direction
		@type activeHigh: bool
		@param startingState: Whether to start enabled or disabled
		@type startingState: bool
		@param debugLevel: logging level
		@type debugLevel: int
		"""
		super(Relay, self).__init__(pin, activeHigh, debugLevel)
		self.logger = getLogger('Relay', debugLevel)
		self.init()
		if startingState:
			self.enable()
		else:
			self.disable()

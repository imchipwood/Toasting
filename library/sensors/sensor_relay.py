import logging

# from setupLogging import getLogger
from library.other.setupLogging import getLogger

try:
	# RPi
	import RPi.GPIO as GPIO
except:
	# Other
	import library.sensors.MockGPIO as GPIO


class Sensor(object):
	def __init__(self, pin, enable=GPIO.HIGH, debugLevel=logging.INFO):
		super(Sensor, self).__init__()

		self.logger = getLogger('Sensor', debugLevel)
		self.debugLevel = debugLevel
		self.state = False
		self._pin = pin
		self.positive = enable
		self.negative = GPIO.LOW if enable == GPIO.HIGH else GPIO.HIGH
		# self.init()

	@property
	def pin(self):
		return self._pin

	@pin.setter
	def pin(self, pin):
		self.cleanup()
		self._pin = pin
		self.init()

	def init(self):
		self.logger.debug("initing pin {}".format(self.pin))
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin, GPIO.OUT)
		self.disable()

	def enable(self):
		GPIO.output(self.pin, self.positive)
		self.state = True

	def disable(self):
		GPIO.output(self.pin, self.negative)
		self.state = False

	def cleanup(self):
		try:
			GPIO.cleanup(self.pin)
			self.logger.debug("GPIO.cleanup({}) complete".format(self.pin))
		except:
			self.logger.exception("issue during GPIO.cleanup()")


class Relay(Sensor):
	def __init__(self, pin, enable=GPIO.HIGH, startingState=False, debugLevel=logging.INFO):
		super(Relay, self).__init__(pin, enable, debugLevel)
		self.logger = getLogger('Relay', debugLevel)
		self.init()
		if startingState:
			self.enable()
		else:
			self.disable()

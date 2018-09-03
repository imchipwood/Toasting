import json
from collections import OrderedDict

from library.control.pid import PID
from library.sensors.sensor_thermocouple import Thermocouple


class ToasterConfig(object):
	BASE_UNITS = "celsius"

	BASE_PINS = {
		"SPI_CS": 0,
		"relay": 4
	}

	BASE_CLOCK_PERIOD = 0.5

	BASE_PID = PID({
		"kP": 0.6,
		"kI": 0.005,
		"kD": 7.0,
		"min": "",
		"max": "",
		"windupGuard": 20.0,
	})

	BASE_STATES = OrderedDict()

	def __init__(self, configPath):
		super(ToasterConfig, self).__init__()

		self.configPath = configPath

		# The params we need to fill
		self._units = self.BASE_UNITS
		self._pins = self.BASE_PINS
		self._pids = self.BASE_PID
		self._clockPeriod = self.BASE_CLOCK_PERIOD
		self._states = self.BASE_STATES

		self._config = OrderedDict()
		if configPath:
			self._config = ToasterConfig.ReadConfig(configPath)
			self.extractConfig()

	@staticmethod
	def ReadConfig(configPath):
		"""
		Read the config file
		@param configPath: path to config file
		@type configPath: str
		@return: JSON dict
		@rtype: dict
		"""
		with open(configPath, "r") as inf:
			return json.load(inf, object_pairs_hook=OrderedDict)

	def extractConfig(self):
		"""
		Convert config dict into class attributes
		@return:
		@rtype:
		"""
		self.units = self.config.get("units", self.BASE_UNITS)
		self._pins = self.config.get("pins", self.BASE_PINS)

		tuning = self.config.get("tuning")
		if tuning:
			pids = tuning.get("pid")
			if pids:
				self.pids = PID(pids)

			clockPeriod = tuning.get("timerPeriod")
			if clockPeriod:
				self._clockPeriod = clockPeriod

		self.states = self.config.get("states", self.BASE_STATES)

	@property
	def config(self):
		return self._config

	@config.setter
	def config(self, configDict):
		self._config = configDict
		self.extractConfig()

	@property
	def units(self):
		return self._units

	@units.setter
	def units(self, units):
		units = Thermocouple.CheckUnits(units)
		self._units = units
		self.config['units'] = self._units

	@property
	def pins(self):
		return self._pins

	@property
	def spiCsPin(self):
		return self.pins.get('SPI_CS')

	@spiCsPin.setter
	def spiCsPin(self, pin):
		pin = Thermocouple.CheckSPICSPin(pin)
		self.pins['SPI_CS'] = pin

	@property
	def relayPin(self):
		return self.pins['relay']

	@relayPin.setter
	def relayPin(self, pin):
		self.pins['relay'] = int(pin)

	@property
	def pids(self):
		return self._pids

	@pids.setter
	def pids(self, pids):
		if isinstance(pids, PID):
			self._pids = pids
		elif isinstance(pids, dict):
			self._pids = PID(pids)
		if 'tuning' not in self.config:
			self.config['tuning'] = {'pid': self.pids.getConfig()}
		else:
			self.config['tuning']['pid'] = self.pids.getConfig()

	@property
	def clockPeriod(self):
		return self._clockPeriod

	@clockPeriod.setter
	def clockPeriod(self, period):
		self._clockPeriod = float(period)
		if 'tuning' not in self.config:
			self.config['tuning'] = {'timerPeriod': self.clockPeriod}
		else:
			self.config['tuning']['timerPeriod'] = self.clockPeriod

	@property
	def states(self):
		return self._states

	@states.setter
	def states(self, states):
		"""
		Set the states
		@param states: dict of states
		@type states: OrderedDict
		"""
		if not isinstance(states, OrderedDict):
			raise TypeError("Incorrect type for states - must be OrderedDict")
		self._states = states
		self.config['states'] = states

	def dumpConfig(self, filePath):
		"""
		Dump the current config to a file
		@param filePath: target file path
		@type filePath: str
		"""
		with open(filePath, 'w') as oup:
			json.dump(self.config, oup, indent=2)

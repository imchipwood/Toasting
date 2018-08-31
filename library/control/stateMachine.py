import csv
import logging
from collections import OrderedDict

from library.other.setupLogging import getLogger
from library.other.config import ToasterConfig
from library.sensors.sensor_relay import Relay
from library.sensors.sensor_thermocouple import Thermocouple
from library.control.pid import PID
from library.ui.visualizer_configuration import CONFIG_KEY_TARGET, CONFIG_KEY_DURATION
from definitions import GetBaseConfigurationFilePath


class STATES:
	RUNNING = 'Running'
	STOPPED = 'Stopped'
	PAUSED = 'Paused'
	TESTING = 'Testing'
	COMPLETE = 'Complete'


class ToastStateMachine(object):
	"""
	State Machine for Toasting2.0
	Two types of states:
	1. Heating/Cooling - state is complete when target temperature is reached, regardless of duration
	2. Soaking - state is complete when duration expires, regardless of target temperature
		Soaking states hold the same temperature reached at the end of the previous state
	"""
	def __init__(self, jsonConfigPath=GetBaseConfigurationFilePath(), stateMachineCompleteCallback=None, debugLevel=logging.INFO):
		"""
		ToastStateMachine Constructor
		@param jsonConfigPath: path to JSON configuration file
		@type jsonConfigPath: str
		@param stateMachineCompleteCallback: callback to use for UI update on reflow completion
		@type stateMachineCompleteCallback: func
		@param debugLevel: logging level
		@type debugLevel: int
		"""
		super(ToastStateMachine, self).__init__()

		self.debugLevel = debugLevel
		self.logger = getLogger('ToastStateMachine', self.debugLevel)

		# Config
		self._config = None
		self.pins = None
		self.relay = None
		self.thermocouple = None

		# Basics of state machine
		self.stateIndex = 0
		self.currentState = None
		self.lastTarget = 0.0
		self.currentStateDuration = 0.0
		self.currentStateEnd = 0.0
		self.stateChanged = False
		self.soaking = False
		self.running = STATES.STOPPED

		# Callback
		self.stateMachineCompleteCallback = stateMachineCompleteCallback

		# Control loop
		self.timestamp = 0.0
		self.lastControlLoopTimestamp = 0.0

		# Sensors
		self.maxTCErrorHistory = 10
		self.recentTCErrors = [None] * self.maxTCErrorHistory

		# PID Controller
		# self.pid = PID(configDict=self.config['tuning']['pid'])

		self.config = jsonConfigPath

		# Data tracking
		self.data = []

	def __repr__(self):
		return "{}:{}".format(self.running, self.currentState)

	# region Properties

	@property
	def stateConfiguration(self):
		"""
		Get the current state configuration
		@return: current state configuration
		@rtype: OrderedDict
		"""
		return self.config.states

	@stateConfiguration.setter
	def stateConfiguration(self, configDict):
		"""
		Set a new state configuration
		@param configDict: new state configuration
		@type configDict: OrderedDict
		"""
		self.config.states = configDict

	@property
	def states(self):
		"""
		Get the names of the configured states
		@return: List of state names
		@rtype: list[str]
		"""
		if self.stateConfiguration:
			return list(self.stateConfiguration.keys())
		else:
			return []

	@property
	def pid(self):
		"""
		Get the PID object
		@return: the current PID object
		@rtype: PID
		"""
		return self.config.pids

	@property
	def timerPeriod(self):
		"""
		Get the current timer period
		@return: current timer period
		@rtype: float
		"""
		return self.config.clockPeriod

	@timerPeriod.setter
	def timerPeriod(self, period):
		"""
		Setter for timer clock period
		@param period: new timer clock period
		@type period: str or int or float
		"""
		self.config.clockPeriod = float(period)

	@property
	def targetState(self):
		"""
		Get the current target state
		@return: current target state
		@rtype: float
		"""
		return self.config.pids.target

	@targetState.setter
	def targetState(self, newTarget):
		"""
		Set a new target state
		@param newTarget: new target state
		@type newTarget: str or int or float
		"""
		self.config.pids.target = newTarget

	@property
	def temperature(self):
		"""
		Get the current thermocouple temperature
		@return: current thermocouple temperature
		@rtype: float
		"""
		return self.thermocouple.temperature

	@property
	def refTemperature(self):
		"""
		Get the current reference temperature
		@return: current reference temperature
		@rtype: float
		"""
		return self.thermocouple.refTemperature

	@property
	def relayState(self):
		"""
		Get the current relay state
		@return: current relay state
		@rtype: bool
		"""
		return self.relay.state

	@property
	def units(self):
		"""
		Get the current units
		@return: current units
		@rtype: str
		"""
		return self.thermocouple.units

	@units.setter
	def units(self, units):
		"""
		Set the current units
		@param units: new units
		@type units: str
		"""
		self.thermocouple.units = units
		self.config.units = units

	# endregion Properties
	# region Configuration

	@property
	def config(self):
		"""
		Get the current config
		@rtype: ToasterConfig
		"""
		return self._config

	@config.setter
	def config(self, configPath):
		"""
		Setup a new configuration
		@param configPath: path to new config file
		@type configPath: str
		"""
		# First attempt to clean up
		try:
			self.cleanup()
		except:
			pass

		# Load in the config file. Most stuff is accessed directly from the configuration
		self._config = ToasterConfig(configPath)

		# Pins
		self.pins = self.config.pins

		# Relay
		if not self.relay:
			self.relay = Relay(self.pins['relay'], debugLevel=self.debugLevel)
		else:
			self.relay.pin = self.config.relayPin

		# Thermocouple
		if not self.thermocouple:
			self.thermocouple = Thermocouple(self.pins['SPI_CS'], debugLevel=self.debugLevel)
		else:
			self.thermocouple.csPin = self.config.spiCsPin

	def dumpConfig(self, filePath):
		"""
		Dump configuration to file
		@param filePath: path to dump JSON config to
		@type filePath: str
		"""
		self.config.dumpConfig(filePath)

	# endregion Configuration
	# region StateMachine
		# region Control

	def start(self):
		"""
		Begin the state machine
		"""
		self.logger.debug("Beginning state machine")
		self.running = STATES.RUNNING
		# reset all the state variables
		self.pid.zeroierror()
		self.timestamp = 0.0
		self.lastControlLoopTimestamp = 0.0
		self.stateIndex = 0
		self.lastTarget = 0.0
		self.updateStateVariables()
		self.data = []
		self.soaking = False

	def stop(self):
		"""
		Stop the state machine
		"""
		self.running = STATES.STOPPED
		self.stateIndex = 0
		self.timestamp = 0.0
		self.lastControlLoopTimestamp = 0.0
		self.lastTarget = 0.0
		self.updateStateVariables()

	def resume(self):
		"""
		Resume a paused state machine
		"""
		self.running = STATES.RUNNING

	def pause(self):
		"""
		Pause a currently running state machine
		"""
		self.running = STATES.PAUSED

		# endregion Control
		# region Loop

	def tick(self, testing=False):
		"""
		Call every tick of clock/timer to increment timestamp
		@param testing: flag to disable relay control
		@type testing: bool (default = False)
		"""
		# read the thermocouple
		try:
			self.recentTCErrors.pop(0)
			temp = self.thermocouple.read()
			self.recentTCErrors.append(None)
		except Exception as e:
			self.recentTCErrors.append(e)
			self.logger.exception("Thermocouple read error")

		# Don't do anything if we're not running
		if self.running not in [STATES.RUNNING, STATES.TESTING]:
			if not testing:
				self.relay.disable()
			return

		# Increment timestamp
		self.timestamp += self.timerPeriod

		# Ready to move to next state?
		if self.readyForNextState():
			# State is done - go to next state
			self.nextState()

		# Control loop @ 1Hz
		if (self.timestamp - self.lastControlLoopTimestamp) >= 1.0:
			self.lastControlLoopTimestamp = self.timestamp

			# Calculate PID output
			self.pid.compute(self.timestamp, self.temperature, self.stateChanged)
			self.stateChanged = False

			if self.stateIndex == len(self.states) - 1:
				# Last state is always a cooling state - force relay off
				self.relay.disable()
			else:
				# Not last state = check PID output
				if self.pid.output > 0.0:
					self.relay.enable()
				else:
					self.relay.disable()

			# only print/update data when the control loop updates
			self.debugPrint()
			self.updateData()

	def readyForNextState(self):
		"""
		Check if we're ready to move to the next state
		@return: bool
		"""
		if self.soaking:
			# We're soaking - has the state duration completed?
			return self.timestamp >= self.currentStateEnd
		else:
			# Not soaking - check if temp has reached target
			return self.checkStateAgainstTarget()

	def checkStateAgainstTarget(self):
		"""
		Check the current temperature against the target temperature based on whether we are ramping or cooling
		@return: whether or not the temperature has reached the target state
		@rtype: bool
		"""
		# +/- 3.0 as a buffer
		celsiusBuffer = 3.0
		fahrenheitBuffer = self.thermocouple.ConvertCelsiusToFahrenheit(celsiusBuffer)
		buffer = celsiusBuffer if self.units == 'celsius' else fahrenheitBuffer
		if self.targetState > self.lastTarget:
			return self.temperature >= self.targetState - buffer
		else:
			return self.temperature <= self.targetState + buffer

	def nextState(self):
		"""
		Move state machine to next state
		"""
		self.logger.debug("{} - moving to next state".format(self.timestamp))
		# Increment state index
		self.stateIndex += 1

		# Check if state machine has reached the end
		if self.stateIndex == len(self.states):
			self.running = STATES.COMPLETE
			if self.stateMachineCompleteCallback:
				self.stateMachineCompleteCallback()

		# Update state variables if we're still running
		if self.running == STATES.RUNNING:
			self.updateStateVariables()

	def updateStateVariables(self):
		"""
		Update the current state variables
		"""
		self.currentState = self.states[self.stateIndex]

		# Get next state info
		self.lastTarget = self.targetState
		self.targetState = float(self.stateConfiguration[self.currentState][CONFIG_KEY_TARGET])
		self.currentStateDuration = float(self.stateConfiguration[self.currentState][CONFIG_KEY_DURATION])

		# Soaking stages simply maintain a steady temperature for a certain duration
		# Heating/Cooling stages have no duration
		self.soaking = self.targetState == self.lastTarget
		self.currentStateEnd = self.timestamp + self.currentStateDuration

		# Zero out the integrated error so it can build up again for this state
		self.pid.zeroierror()
		self.stateChanged = True

		if self.running not in [STATES.STOPPED, STATES.PAUSED]:
			self.logger.debug(
				"New state, target, end timestamp: {}, {:7.2f}, {}".format(
					self.currentState,
					self.targetState,
					"{:7.2f}".format(self.currentStateEnd) if self.soaking else "    n/a"
				)
			)

		# endregion Loop
	# endregion StateMachine
	# region Data

	def getRecentErrorCount(self):
		"""
		Get the number of recent errors
		@return: number of recent errors
		@rtype: int
		"""
		return len([error for error in self.recentTCErrors if error is not None])

	def debugPrint(self):
		"""
		Print debug info to screen
		"""
		self.logger.debug(
			"{:7.2f}, {}, {}".format(
				self.timestamp,
				"{:7.2f}".format(self.currentStateEnd) if self.soaking else "    n/a",
				self.pid.currentStateToString()
			)
		)

	def updateData(self):
		"""
		Update data tracking
		"""
		# Build data dict
		data = {
			'Timestamp': self.timestamp,
			'Temperature': self.temperature,
			'Target Temperature': self.targetState,
			'State': self.currentState,
			'Relay State': self.relay.state,
			'PID Output': self.pid.output,
			'PID Error': self.pid.error,
			'PID IError': self.pid.ierror,
			'PID DError': self.pid.derror,
		}
		self.data.append(data)

	def dumpDataToCsv(self, csvPath):
		"""
		Dump data to a CSV file
		@param csvPath: path to CSV file to dump data to
		@type csvPath: str
		@return: True if successful, False otherwise
		@rtype: bool
		"""
		if not self.data:
			return False

		# write to file
		header = [
			'Timestamp',
			'Temperature',
			'Target Temperature',
			'State',
			'Relay State',
			'PID Output',
			'PID Error',
			'PID IError',
			'PID DError',
		]
		with open(csvPath, 'w', newline="") as ouf:
			writer = csv.DictWriter(ouf, fieldnames=header)
			writer.writeheader()
			writer.writerows(self.data)

		return True

	# endregion Data
	# region GPIO

	def cleanup(self):
		"""
		Clean up all GPIO
		"""
		self.relay.disable()
		self.thermocouple.cleanup()
		self.relay.cleanup()

	# endregion GPIO

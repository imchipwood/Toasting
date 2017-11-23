import csv
import logging

from library.other.setupLogging import getLogger
from library.sensors.sensor_relay import Relay
from library.sensors.sensor_thermocouple import Thermocouple
from library.control.pid import PID
from library.ui.visualizer_configuration import CONFIG_KEY_TARGET, CONFIG_KEY_DURATION


class ToastStateMachine(object):
	"""State Machine for Toasting2.0

	Two types of states:
	1. Heating/Cooling - state is complete when target temperature is reached, regardless of duration
	2. Soaking - state is complete when duration expires, regardless of target temperature
		Soaking states hold the same temperature reached at the end of the previous state

	"""
	def __init__(self, stateConfiguration, timerPeriod, csPin, relayPin, stateMachineCompleteCallback=None, pidTuning={}, debugLevel=logging.INFO):
		super(ToastStateMachine, self).__init__()

		self.logger = getLogger('ToastStateMachine', debugLevel)

		self.states = None
		self.stateConfiguration = stateConfiguration
		# self.states = self._stateConfiguration.keys()
		self.stateIndex = 0

		self.timestamp = 0.0
		self.lastControlLoopTimestamp = 0.0
		self.timerPeriod = timerPeriod

		self.currentState = None
		self.lastTarget = 0.0
		self.currentStateDuration = 0.0
		self.currentStateEnd = 0.0

		self.thermocouple = Thermocouple(csPin, debugLevel=debugLevel)
		self.relay = Relay(relayPin, debugLevel=debugLevel)

		self.stateMachineCompleteCallback = stateMachineCompleteCallback

		self.soaking = False
		self.runningStates = ['Running', 'Paused', 'Stopped']
		self.running = 'Stopped'

		self.maxTCErrorHistory = 10
		self.recentTCErrors = [None] * self.maxTCErrorHistory

		kP = pidTuning['kP']
		kI = pidTuning['kI']
		kD = pidTuning['kD']
		minLimit = pidTuning['min']
		if minLimit == u'':
			minLimit = None
		maxLimit = pidTuning['max']
		if maxLimit == u'':
			maxLimit = None
		maxIError = pidTuning['maxierror']
		if maxIError == u'':
			maxIError = None

		self.pid = PID(
			p=kP,
			i=kI,
			d=kD,
			minLimit=minLimit,
			maxLimit=maxLimit,
			target=0.0,
			maxIError=maxIError
		)

		self.data = []

	# region Properties

	@property
	def stateConfiguration(self):
		return self._stateConfiguration

	@stateConfiguration.setter
	def stateConfiguration(self, configDict):
		self._stateConfiguration = configDict
		try:
			self.logger.debug("updating states")
			self.states = list(self.stateConfiguration.keys())
			self.logger.debug("new states: {}".format(self.states))
		except:
			pass

	@property
	def target(self):
		return self.pid.target

	@target.setter
	def target(self, newTarget):
		self.pid.target = newTarget

	@property
	def temperature(self):
		return self.thermocouple.temperature

	@property
	def refTemperature(self):
		return self.thermocouple.refTemperature

	@property
	def relayState(self):
		return self.relay.state

	# endregion Properties

	def cleanup(self):
		"""Clean up all GPIO"""
		self.relay.disable()
		self.thermocouple.cleanup()
		self.relay.cleanup()

	# region StateMachine

	def start(self):
		"""Begin the state machine"""
		self.logger.info("Beginning state machine")
		self.running = 'Running'
		# reset all the state variables
		self.pid.zeroierror()
		self.timestamp = 0.0
		self.lastControlLoopTimestamp = 0.0
		self.stateIndex = 0
		self.updateState()
		self.lastTarget = 0.0
		self.data = []

	def stop(self):
		"""Stop the state machine"""
		self.running = 'Stopped'
		self.stateIndex = 0
		self.timestamp = 0.0
		self.lastControlLoopTimestamp = 0.0
		self.updateState()
		self.lastTarget = 0.0

	def resume(self):
		"""Resume a paused state machine"""
		self.running = 'Running'

	def pause(self):
		"""Pause a currently running state machine"""
		self.running = 'Paused'

	def getRecentErrorCount(self):
		"""Count # of recent errors

		@return: int
		"""
		return len([error for error in self.recentTCErrors if error is not None])

	def tick(self, testing=False):
		"""Call every tick of clock/timer to increment timestamp"""
		# read the thermocouple
		try:
			self.recentTCErrors.pop(0)
			temp = self.thermocouple.read()
			self.recentTCErrors.append(None)
		except Exception as e:
			self.recentTCErrors.append(e)
			self.logger.exception("Thermocouple read error")

		# Don't do anything if we're not running
		if self.running not in ['Running', 'Testing']:
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
		# if (self.timestamp - self.lastControlLoopTimestamp) >= 1.0:
		if True:
			self.lastControlLoopTimestamp = self.timestamp

			# Calculate PID output
			self.pid.compute(self.timestamp, self.temperature)

			if self.stateIndex == len(self.states):
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
		"""Check if we're ready to move to the next state

		@return: bool
		"""
		if self.soaking:
			if self.timestamp >= self.currentStateEnd:
				return True
		else:
			if self.target > self.lastTarget and self.temperature >= self.target:
				return True
			elif self.target < self.lastTarget and self.temperature <= self.target:
				return True

		# Nope, not ready
		return False

	def nextState(self):
		"""Move state machine to next state"""
		self.logger.info("moving to next state")
		# Increment state index
		self.stateIndex += 1

		# Check if state machine has reached the end
		if self.stateIndex == len(self.states) + 1:
			self.running = 'Complete'
			if self.stateMachineCompleteCallback:
				self.stateMachineCompleteCallback()
			return

		# Update state variables if we're still running
		if self.running == 'Running':
			self.updateState()

	def updateState(self):
		"""Update the current state variables"""
		self.currentState = self.states[self.stateIndex]

		self.lastTarget = self.target
		self.target = float(self._stateConfiguration[self.currentState][CONFIG_KEY_TARGET])
		self.currentStateDuration = float(self._stateConfiguration[self.currentState][CONFIG_KEY_DURATION])

		# Soaking stages simply maintain a steady temperature for a certain duration
		# Heating/Cooling stages have no duration
		self.soaking = self.target == self.lastTarget
		self.currentStateEnd = self.timestamp + self.currentStateDuration

		if self.stateIndex != 0:
			stateEnd = "{:7.2f}".format(self.currentStateEnd)
			self.logger.info(
				"New state, target, end timestamp: {:7.2f}, {:7.2f}, {}".format(
					self.currentState,
					self.target,
					stateEnd if self.soaking else " n/a"
				)
			)

	# endregion StateMachine
	# region Data

	def debugPrint(self):
		"""Print debug info to screen"""
		stateEnd = "{:7.2f}".format(self.currentStateEnd)
		self.logger.debug(
			"{:7.2f}, {}, {:7.2f}, {:7.2f}, {:7.2f}, {:7.2f}, {:7.2f}, {:7.2f}".format(
				self.timestamp,
				stateEnd if self.soaking else " n/a",
				self.pid.state,
				self.pid.target,
				self.pid.error,
				self.pid.ierror,
				self.pid.derror,
				self.pid.output
			)
		)

	def updateData(self):
		"""Update data tracking"""
		# Build data dict
		data = {
			'Timestamp': self.timestamp,
			'Temperature': self.temperature,
			'Target Temperature': self.target,
			'State': self.currentState,
			'PID Output': self.pid.output,
			'PID Error': self.pid.error,
			'PID IError': self.pid.ierror,
			'PID DError': self.pid.derror,
		}
		self.data.append(data)

	def dumpDataToCsv(self, csvPath):
		"""Dump data to a CSV file

		@param csvPath: path to CSV file to dump data to
		@type csvPath: str
		@return: bool - True if successful, False otherwise
		"""
		if not self.data:
			return False

		# write to file
		header = [
			'Timestamp',
			'Temperature',
			'Target Temperature',
			'State',
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

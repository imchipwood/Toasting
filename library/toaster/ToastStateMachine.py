import logging

from library.other.setupLogging import getLogger
from library.sensors.sensor_relay import Relay
from library.sensors.sensor_thermocouple import Thermocouple
from library.toaster.pid import PID
from library.ui.ConfigurationVisualizer import CONFIG_KEY_TARGET, CONFIG_KEY_DURATION


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
		self.timerPeriod = timerPeriod

		self.currentState = None
		self.currentTarget = 0.0
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

		self.pid = PID(
			p=kP,
			i=kI,
			d=kD,
			minLimit=minLimit,
			maxLimit=maxLimit,
			target=self.currentTarget
		)

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
	def temperature(self):
		return self.thermocouple.temperature

	@property
	def refTemperature(self):
		return self.thermocouple.refTemperature

	@property
	def units(self):
		return self.thermocouple.units

	@units.setter
	def units(self, units):
		self.thermocouple.units = units

	def start(self):
		self.running = 'Running'
		self.timestamp = 0.0
		self.stateIndex = 0
		self.updateState()
		self.lastTarget = 0.0

	def stop(self):
		self.running = 'Stopped'
		self.stateIndex = 0
		self.updateState()
		self.lastTarget = 0.0

	def resume(self):
		self.running = 'Running'

	def pause(self):
		self.running = 'Paused'

	def getRecentErrorCount(self):
		return len([error for error in self.recentTCErrors if error is not None])

	def tick(self, testing=False):
		"""Call every tick of clock/timer to increment timestamp"""
		# read the thermocouple
		try:
			self.recentTCErrors.pop(0)
			self.thermocouple.read()
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
		if self.soaking and self.timestamp >= self.currentStateEnd or self.temperature == self.currentTarget:
			# State is done - go to next state
			self.nextState()

		# Calculate PID output
		pidOut = self.pid.compute(self.timestamp, self.temperature)
		# self.logger.debug("pidout: {}".format(pidOut))

		# Control relay @ 1Hz
		if self.timestamp % 1 == 0:
			if pidOut > 0.0:
				if not self.relay.state:
					self.logger.debug("enabling relay")
					self.relay.enable()
			else:
				if self.relay.state:
					self.logger.debug("disabling relay")
					self.relay.disable()

	def nextState(self):
		"""Move state machine to next state"""
		self.stateIndex += 1

		# Have we reached the end of the state machine?
		if self.stateIndex == len(self.states):
			self.running = 'Complete'
			if self.stateMachineCompleteCallback:
				self.stateMachineCompleteCallback()
			return

		if self.running == 'Running':
			self.updateState()

	def updateState(self):
		self.currentState = self.states[self.stateIndex]

		self.lastTarget = self.currentTarget
		self.currentTarget = self._stateConfiguration[self.currentState][CONFIG_KEY_TARGET]
		self.currentStateDuration = self._stateConfiguration[self.currentState][CONFIG_KEY_DURATION]
		self.currentStateEnd += self.currentStateDuration

		# Soaking stages simply maintain a steady temperature for a certain duration
		# Heating/Cooling stages hav
		self.soaking = self.currentTarget == self.lastTarget

		# update target for PID
		self.pid.target = self.currentTarget

	def cleanup(self):
		self.relay.disable()
		self.thermocouple.cleanup()
		self.relay.cleanup()

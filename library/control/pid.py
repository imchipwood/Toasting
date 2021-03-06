from collections import OrderedDict


class PID(object):
	def __init__(self, configDict=None):
		super(PID, self).__init__()

		self._kP = 0.0
		self._kI = 0.0
		self._kD = 0.0

		self._windupGuard = 0.0

		self._currentState = 0.0
		self._targetState = 0.0

		self._output = 0.0
		self._error = 0.0
		self._lastError = 0.0
		self._iError = 0.0
		self._dError = 0.0

		self._deltaTime = 0.0
		self._lastTime = 0.0

		self._min = None
		self._max = None

		if configDict:
			self.setConfig(configDict)

	# region Gains

	@property
	def kP(self):
		return self._kP

	@kP.setter
	def kP(self, kP):
		self._kP = float(kP)

	@property
	def kI(self):
		return self._kI

	@kI.setter
	def kI(self, kI):
		self._kI = float(kI)

	@property
	def kD(self):
		return self._kD

	@kD.setter
	def kD(self, kD):
		self._kD = float(kD)

	# endregion Gains
	# region States
		
	@property
	def state(self):
		return self._currentState

	@property
	def target(self):
		return self._targetState

	@target.setter
	def target(self, target):
		self._targetState = float(target)

	@property
	def output(self):
		return self._output

	@output.setter
	def output(self, val):
		"""Output Setter - apply limits"""
		if val > self.max:
			val = self.max
		elif val < self.min:
			val = self.min
		self._output = val

	@property
	def error(self):
		return self._error

	@property
	def ierror(self):
		return self._iError

	@property
	def derror(self):
		return self._dError

	# endregion States
	# region Limits

	@property
	def windupGuard(self):
		return self._windupGuard

	@windupGuard.setter
	def windupGuard(self, windupGuard):
		if windupGuard is not None:
			self._windupGuard = float(windupGuard)
		else:
			self._windupGuard = None

	@property
	def min(self):
		return self._min

	@min.setter
	def min(self, minVal):
		"""Min Setter - force less than max"""
		if self.max:
			assert self.min < self.max
		if minVal is not None:
			self._min = float(minVal)
		else:
			self._min = minVal

	@property
	def max(self):
		return self._max

	@max.setter
	def max(self, maxVal):
		"""Max Setter - force greater than min"""
		if self.min:
			assert self.min < self.max
		if maxVal is not None:
			self._max = float(maxVal)
		else:
			self._max = maxVal

	# endregion Limits
	# region Config

	def setConfig(self, configDict):
		"""Set new config for PID controller

		@param configDict: dict of PID parameters
		"""
		self.kP = configDict['kP']
		self.kI = configDict['kI']
		self.kD = configDict['kD']
		self.min = configDict['min'] if configDict['min'] != "" else None
		self.max = configDict['max'] if configDict['max'] != "" else None
		self.windupGuard = configDict['windupGuard'] if configDict['windupGuard'] != "" else None
		self.zeroierror()

	def getConfig(self):
		"""Return current PID settings as dict"""
		config = OrderedDict()
		config['kP'] = self.kP
		config['kI'] = self.kI
		config['kD'] = self.kD
		config['min'] = "" if self.min is None else self.min
		config['max'] = "" if self.max is None else self.max
		config['windupGuard'] = "" if self.windupGuard is None else self.windupGuard
		return config

	# endregion Config
	# region Execution

	def compute(self, currenttime, currentstate=None, newState=False):
		"""Compute the output of the PID controller based on the elapsed time and the current target

		@param currenttime: the time at which the latest input was sampled
		@type currenttime: float
		@param currentstate: (Optional) current state of device PID controller is controlling. otherwise uses self._currentState
		@type currentstate: float

		@return: float
		"""
		if not self.target:
			raise Exception("No target state set, cannot compute PID output")

		# calculate change in time
		self._deltaTime = currenttime - self._lastTime

		# update state if available
		if currentstate:
			self._currentState = currentstate

		# proportional error from target
		self._error = self.target - self.state
		# integral of error from target
		self._iError += self.error * self._deltaTime

		# windup guard for integrated error
		if self.windupGuard:
			if self.ierror < -self.windupGuard:
				self._iError = -self.windupGuard
			if self.ierror > self.windupGuard:
				self._iError = self.windupGuard

		# derivative of error from target
		if newState:
			# force derivative to 0 if we just changed states
			self._dError = 0.0
		else:
			# derivative is slope of error over time
			self._dError = (self.error - self._lastError) / self._deltaTime

		# apply gains to error values
		self._output = self.kP * self.error + self.kI * self.ierror + self.kD * self.derror

		self._lastTime = currenttime
		self._lastError = self.error

		return self.output

	def zeroierror(self):
		self._iError = 0.0

	# endregion Execution

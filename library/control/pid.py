from collections import OrderedDict


class PID(object):

	def __init__(self, configDict=None):
		"""
		Constructor for PID object
		@param configDict: Configuration dict of PID parameters
		@type configDict: dict
		"""
		super(PID, self).__init__()

		# Gains
		self._kP = 0.0
		self._kI = 0.0
		self._kD = 0.0
		self._windupGuard = 0.0

		# State
		self._currentState = 0.0
		self._targetState = 0.0
		self._output = 0.0

		# Error variables
		self._error = 0.0
		self._lastError = 0.0
		self._iError = 0.0
		self._dError = 0.0

		# Limits
		self._min = None
		self._max = None

		# Time
		self._lastTime = 0.0

		# Load the config
		if configDict:
			self.setConfig(configDict)

	# region Gains

	@property
	def kP(self):
		"""
		@rtype: float
		"""
		return self._kP

	@kP.setter
	def kP(self, kp):
		"""
		Set the proportional gain
		@param kp: new proportional gain
		@type kp: str or int or float
		"""
		try:
			self._kP = float(kp)
		except ValueError:
			raise ValueError("Failed to convert PID proportional gain input value '{}' to a float".format(kp))

	@property
	def kI(self):
		"""
		@rtype: float
		"""
		return self._kI

	@kI.setter
	def kI(self, ki):
		"""
		Set the integrated gain
		@param ki: new integrated gain
		@type ki: str or int or float
		"""
		try:
			self._kI = float(ki)
		except ValueError:
			raise ValueError("Failed to convert PID integral gain input value '{}' to a float".format(ki))

	@property
	def kD(self):
		"""
		@rtype: float
		"""
		return self._kD

	@kD.setter
	def kD(self, kd):
		"""
		Set the derivative gain
		@param kd: new derivative gain
		@type kd: str or int or float
		"""
		try:
			self._kD = float(kd)
		except ValueError:
			raise ValueError("Failed to convert PID derivative gain input value '{}' to a float".format(kd))

	# endregion Gains
	# region States
		
	@property
	def state(self):
		"""
		@rtype: float
		"""
		return self._currentState

	@property
	def target(self):
		"""
		@rtype: float
		"""
		return self._targetState

	@target.setter
	def target(self, target):
		"""
		Set a new target state
		@param target: new target state
		@type target: str or int or float
		"""
		self._targetState = float(target)

	@property
	def output(self):
		"""
		@rtype: float
		"""
		return self._output

	@output.setter
	def output(self, val):
		"""
		Output Setter - apply limits
		@param val: new output value
		@type val: float or int
		"""
		if self.max is not None and val > self.max:
			val = self.max
		elif self.min is not None and val < self.min:
			val = self.min
		self._output = val

	@property
	def error(self):
		"""
		@rtype: float
		"""
		return self._error

	@property
	def ierror(self):
		"""
		@rtype: float
		"""
		return self._iError

	@ierror.setter
	def ierror(self, ierror):
		"""
		Setter for integrated error
		Applies windup guard automatically
		@param ierror: new integrated error
		@type ierror: float
		"""
		self._iError = ierror
		self.applyWindup()

	@property
	def derror(self):
		"""
		@rtype: float
		"""
		return self._dError

	# endregion States
	# region Limits

	@property
	def windupGuard(self):
		"""
		@rtype: float
		"""
		return self._windupGuard

	@windupGuard.setter
	def windupGuard(self, windupGuard):
		"""
		Set the Integrated error windup guard
		@param windupGuard: new windup guard
		@type windupGuard: str or int or float
		"""
		if windupGuard is not None:
			try:
				self._windupGuard = abs(float(windupGuard))
			except ValueError:
				raise ValueError("Failed to convert PID windup guard input value '{}' to a float".format(windupGuard))
		else:
			self._windupGuard = None

	@property
	def min(self):
		"""
		@rtype: float
		"""
		return self._min

	@min.setter
	def min(self, minLimit):
		"""
		Min Setter - force less than max
		Raises exception if min is greater than max
		@param minLimit: new minimum output value
		@type minLimit: float or int
		"""
		# Check for valid value
		if minLimit in ['', None]:
			self._min = None
			return

		# Convert to float
		try:
			minLimit = float(minLimit)
		except ValueError:
			raise ValueError("Failed to convert PID min limit input value '{}' to a float".format(minLimit))

		# Check validity against max limit
		if self.max is not None:
			assert minLimit < self.max, "Min limit must be lower than max: {}".format(self.max)

		# Apply
		self._min = minLimit

	@property
	def max(self):
		"""
		@rtype: float
		"""
		return self._max

	@max.setter
	def max(self, maxLimit):
		"""
		Max Setter - force greater than min
		Raises exception if max is lower than min
		@param maxLimit: new maximum output value
		@type maxLimit: float or int
		"""
		# Check for valid value
		if maxLimit in ['', None]:
			self._max = None
			return

		# Convert to float
		try:
			maxLimit = float(maxLimit)
		except ValueError:
			raise ValueError("Failed to convert PID max limit input value '{}' to a float".format(maxLimit))

		# Check validity against max limit
		if self.min is not None:
			assert self.min < maxLimit, "Max limit must be higher than min: {}".format(self.min)

		# Apply
		self._max = maxLimit

	# endregion Limits
	# region Config

	def setConfig(self, configDict):
		"""
		Set new config for PID controller
		@param configDict: dict of PID parameters
		@type configDict: dict[str, float]
		"""
		self.kP = configDict.get('kP', self.kP)
		self.kI = configDict.get('kI', self.kI)
		self.kD = configDict.get('kD', self.kD)
		self.min = configDict.get('min', self.min)
		self.max = configDict.get('max', self.max)
		self.windupGuard = configDict.get('windupGuard', self.windupGuard)
		self.zeroierror()

	def getConfig(self):
		"""
		Return current PID settings as dict
		"""
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
		"""
		Compute the output of the PID controller based on the elapsed time and the current target
		@param currenttime: the time at which the latest input was sampled
		@type currenttime: float
		@param currentstate: (Optional) current state of device PID controller is controlling. otherwise uses self._currentState
		@type currentstate: float
		@param newState: flag to indicate we're moving to a new state (resets derivative error)
		@type newState: bool
		@return: output of PID computation
		@rtype: float
		"""
		if not self.target:
			raise Exception("No target state set, cannot compute PID output")

		# update state if available
		if currentstate is not None:
			self._currentState = currentstate

		# calculate change in time
		deltaTime = currenttime - self._lastTime

		# proportional error from target
		self._error = self.target - self.state
		# integral of error from target
		self.ierror += self.error * deltaTime

		# derivative of error from target
		if newState or deltaTime == 0:
			# force derivative to 0 if we just changed states
			self._dError = 0.0
		else:
			# derivative is slope of error over time
			self._dError = (self.error - self._lastError) / deltaTime

		# apply gains to error values
		self.output = self.kP * self.error + self.kI * self.ierror + self.kD * self.derror

		self._lastTime = currenttime
		self._lastError = self.error

		return self.output

	def resetClock(self, targetTime=0.0):
		"""
		Reset the time
		@param targetTime: new time to set (default 0.0)
		@type targetTime: str or int or float
		"""
		self._lastTime = float(targetTime)

	def applyWindup(self):
		"""
		Apply the windup guard to the integrated error
		"""
		if self.windupGuard:
			if self.ierror < -self.windupGuard:
				self._iError = -self.windupGuard
			if self.ierror > self.windupGuard:
				self._iError = self.windupGuard

	def zeroierror(self):
		"""
		Zero out the integrated error
		"""
		self.ierror = 0.0

	def currentStateToString(self):
		"""
		Return the current state as a string
		@return: string with current state, target state, all errors, and current output
		@rtype: str
		"""
		return "{:7.2f}, {:7.2f}, {:7.2f}, {:7.2f}, {:7.2f}, {:7.2f}".format(
			self.state,
			self.target,
			self.error,
			self.ierror,
			self.derror,
			self.output
		)

	# endregion Execution

from collections import OrderedDict


class PID(object):
	def __init__(self, p, i, d, minLimit=None, maxLimit=None, target=None):
		super(PID, self).__init__()
		self._kP = float(p)
		self._kI = float(i)
		self._kD = float(d)

		self._currentState = 0.0
		self._targetState = target
		self._interval = 10.0

		self._output = 0.0
		self._error = 0.0
		self._lastError = 0.0
		self._iError = 0.0

		self._deltaTime = 0.0
		self._lastTime = 0.0

		self._min = minLimit
		self._max = maxLimit

	# region PIDProperties

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

	# endregion PIDProperties
	# region StateProperties
		
	@property
	def state(self):
		return self._currentState

	@state.setter
	def state(self, state):
		self._currentState = float(state)

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

	# endregion StateProperties
	# region OtherProperties

	@property
	def interval(self):
		return self._interval

	@interval.setter
	def interval(self, intervalInHz):
		self._interval = float(intervalInHz)

	@property
	def min(self):
		return self._min

	@min.setter
	def min(self, minVal):
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
		if self.min:
			assert self.min < self.max
		if maxVal is not None:
			self._max = float(maxVal)
		else:
			self._max = maxVal

	def getConfig(self):
		config = OrderedDict()
		config['kP'] = self.kP
		config['kI'] = self.kI
		config['kD'] = self.kD
		config['min'] = "" if self.min is None else self.min
		config['max'] = "" if self.max is None else self.max
		return config

	# endregion OtherProperties
	# region Execution

	def compute(self, currenttime, currentstate=None):
		"""Compute the output of the PID controller based on the elapsed time and the current target

		@param currenttime: the time at which the latest input was sampled
		@type currenttime: float
		@param currentstate: (Optional) current state of device PID controller is controlling. otherwise uses self._currentState
		@type currentstate: float

		@return: float
		"""
		if not self.target:
			raise StandardError("No target state set, cannot compute PID output")

		self._deltaTime = currenttime - self._lastTime
		if currentstate:
			self.state = currentstate

		# proportional error from target
		self._error = self.target - self.state
		# integral of error from target
		self._iError += self._error * self._deltaTime
		# derivative of error from target
		if self._deltaTime > 0:
			# multiply seconds by freq in hz to ....? not sure what's going on right here
			#TODO: Check if derivative error calculation is reasonable - the time portion seems funky
			derror = (self.state - self._lastError) / (self._deltaTime * self.interval * 10.0)
		else:
			# match timing loop
			derror = self.state - self._lastError

		# apply gains to error values
		self._output = self.kP * self._error + self.kI * self._iError - self.kD * derror

		self._lastTime = currenttime
		self._lastError = self._error

		return self.output

	def zeroierror(self):
		self._iError = 0.0

	# endregion Execution
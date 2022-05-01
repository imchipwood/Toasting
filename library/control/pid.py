from collections import OrderedDict


class PID:

	def __init__(self, config_dict: dict = None):
		"""
		Constructor for PID object
		@param config_dict: Configuration dict of PID parameters
		@type config_dict: dict
		"""
		super().__init__()

		# Gains
		self._k_p = 0.0
		self._k_i = 0.0
		self._k_d = 0.0
		self._windup_guard = 0.0

		# State
		self._current_state = 0.0
		self._target_state = 0.0
		self._output = 0.0

		# Error variables
		self._error = 0.0
		self._last_error = 0.0
		self._i_error = 0.0
		self._d_error = 0.0

		# Limits
		self._min = None
		self._max = None

		# Time
		self._last_time = 0.0

		# Load the config
		if config_dict:
			self.set_config(config_dict)

	# region Gains

	@property
	def k_p(self):
		"""
		@rtype: float
		"""
		return self._k_p

	@k_p.setter
	def k_p(self, kp):
		"""
		Set the proportional gain
		@param kp: new proportional gain
		@type kp: str or int or float
		"""
		try:
			self._k_p = float(kp)
		except ValueError:
			raise ValueError("Failed to convert PID proportional gain input value '{}' to a float".format(kp))

	@property
	def k_i(self):
		"""
		@rtype: float
		"""
		return self._k_i

	@k_i.setter
	def k_i(self, ki):
		"""
		Set the integrated gain
		@param ki: new integrated gain
		@type ki: str or int or float
		"""
		try:
			self._k_i = float(ki)
		except ValueError:
			raise ValueError("Failed to convert PID integral gain input value '{}' to a float".format(ki))

	@property
	def k_d(self):
		"""
		@rtype: float
		"""
		return self._k_d

	@k_d.setter
	def k_d(self, kd):
		"""
		Set the derivative gain
		@param kd: new derivative gain
		@type kd: str or int or float
		"""
		try:
			self._k_d = float(kd)
		except ValueError:
			raise ValueError("Failed to convert PID derivative gain input value '{}' to a float".format(kd))

	# endregion Gains
	# region States
		
	@property
	def state(self):
		"""
		@rtype: float
		"""
		return self._current_state

	@property
	def target(self):
		"""
		@rtype: float
		"""
		return self._target_state

	@target.setter
	def target(self, target):
		"""
		Set a new target state
		@param target: new target state
		@type target: str or int or float
		"""
		self._target_state = float(target)

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
	def i_error(self):
		"""
		@rtype: float
		"""
		return self._i_error

	@i_error.setter
	def i_error(self, i_error):
		"""
		Setter for integrated error
		Applies windup guard automatically
		@param i_error: new integrated error
		@type i_error: float
		"""
		self._i_error = i_error
		self.apply_windup()

	@property
	def d_error(self):
		"""
		@rtype: float
		"""
		return self._d_error

	# endregion States
	# region Limits

	@property
	def windup_guard(self):
		"""
		@rtype: float
		"""
		return self._windup_guard

	@windup_guard.setter
	def windup_guard(self, windup_guard):
		"""
		Set the Integrated error windup guard
		@param windup_guard: new windup guard
		@type windup_guard: str or int or float
		"""
		if windup_guard is not None:
			try:
				self._windup_guard = abs(float(windup_guard))
			except ValueError:
				raise ValueError("Failed to convert PID windup guard input value '{}' to a float".format(windup_guard))
		else:
			self._windup_guard = None

	@property
	def min(self):
		"""
		@rtype: float
		"""
		return self._min

	@min.setter
	def min(self, min_limit):
		"""
		Min Setter - force less than max
		Raises exception if min is greater than max
		@param min_limit: new minimum output value
		@type min_limit: float or int
		"""
		# Check for valid value
		if min_limit in ['', None]:
			self._min = None
			return

		# Convert to float
		try:
			min_limit = float(min_limit)
		except ValueError:
			raise ValueError("Failed to convert PID min limit input value '{}' to a float".format(min_limit))

		# Check validity against max limit
		if self.max is not None:
			assert min_limit < self.max, "Min limit must be lower than max: {}".format(self.max)

		# Apply
		self._min = min_limit

	@property
	def max(self):
		"""
		@rtype: float
		"""
		return self._max

	@max.setter
	def max(self, max_limit):
		"""
		Max Setter - force greater than min
		Raises exception if max is lower than min
		@param max_limit: new maximum output value
		@type max_limit: float or int
		"""
		# Check for valid value
		if max_limit in ['', None]:
			self._max = None
			return

		# Convert to float
		try:
			max_limit = float(max_limit)
		except ValueError:
			raise ValueError("Failed to convert PID max limit input value '{}' to a float".format(max_limit))

		# Check validity against max limit
		if self.min is not None:
			assert self.min < max_limit, "Max limit must be higher than min: {}".format(self.min)

		# Apply
		self._max = max_limit

	# endregion Limits
	# region Config

	def set_config(self, config_dict):
		"""
		Set new config for PID controller
		@param config_dict: dict of PID parameters
		@type config_dict: dict[str, float]
		"""
		self.k_p = config_dict.get('kP', self.k_p)
		self.k_i = config_dict.get('kI', self.k_i)
		self.k_d = config_dict.get('kD', self.k_d)
		self.min = config_dict.get('min', self.min)
		self.max = config_dict.get('max', self.max)
		self.windup_guard = config_dict.get('windupGuard', self.windup_guard)
		self.zero_i_error()

	def get_config(self):
		"""
		Return current PID settings as dict
		"""
		config = OrderedDict()
		config['kP'] = self.k_p
		config['kI'] = self.k_i
		config['kD'] = self.k_d
		config['min'] = "" if self.min is None else self.min
		config['max'] = "" if self.max is None else self.max
		config['windupGuard'] = "" if self.windup_guard is None else self.windup_guard
		return config

	# endregion Config
	# region Execution

	def compute(self, current_time, current_state=None, new_state=False):
		"""
		Compute the output of the PID controller based on the elapsed time and the current target
		@param current_time: the time at which the latest input was sampled
		@type current_time: float
		@param current_state: (Optional) current state of device PID controller is controlling. otherwise uses self._currentState
		@type current_state: float
		@param new_state: flag to indicate we're moving to a new state (resets derivative error)
		@type new_state: bool
		@return: output of PID computation
		@rtype: float
		"""
		if not self.target:
			raise Exception("No target state set, cannot compute PID output")

		# update state if available
		if current_state is not None:
			self._current_state = current_state

		# calculate change in time
		delta_time = current_time - self._last_time

		# proportional error from target
		self._error = self.target - self.state
		# integral of error from target
		self.i_error += self.error * delta_time

		# derivative of error from target
		if new_state or delta_time == 0:
			# force derivative to 0 if we just changed states
			self._d_error = 0.0
		else:
			# derivative is slope of error over time
			self._d_error = (self.error - self._last_error) / delta_time

		# apply gains to error values
		self.output = self.k_p * self.error + self.k_i * self.i_error + self.k_d * self.d_error

		self._last_time = current_time
		self._last_error = self.error

		return self.output

	def reset_clock(self, target_time=0.0):
		"""
		Reset the time
		@param target_time: new time to set (default 0.0)
		@type target_time: str or int or float
		"""
		self._last_time = float(target_time)

	def apply_windup(self):
		"""
		Apply the windup guard to the integrated error
		"""
		if self.windup_guard:
			if self.i_error < -self.windup_guard:
				self._i_error = -self.windup_guard
			if self.i_error > self.windup_guard:
				self._i_error = self.windup_guard

	def zero_i_error(self):
		"""
		Zero out the integrated error
		"""
		self.i_error = 0.0

	def __repr__(self):
		"""
		Return the current state as a string
		@return: string with current state, target state, all errors, and current output
		@rtype: str
		"""
		return "{:7.2f}, {:7.2f}, {:7.2f}, {:7.2f}, {:7.2f}, {:7.2f}".format(
			self.state,
			self.target,
			self.error,
			self.i_error,
			self.d_error,
			self.output
		)

	# endregion Execution

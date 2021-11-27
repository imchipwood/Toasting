from collections import OrderedDict


class PID:
	def __init__(self, config_dict: dict[str, float or str] = None):
		"""
		Proportional-Integral-Derivative controller
		@param config_dict: dict of PID parameters
		"""
		super()

		self._k_p = 0.0
		self._k_i = 0.0
		self._k_d = 0.0

		self._windup_guard = 0.0

		self._current_state = 0.0
		self._target_state = 0.0

		self._output = 0.0
		self._error = 0.0
		self._last_error = 0.0
		self._i_error = 0.0
		self._d_error = 0.0

		self._delta_time = 0.0
		self._last_time = 0.0

		self._min = None
		self._max = None

		if config_dict:
			self.set_config(config_dict)

	# region Gains

	@property
	def k_p(self) -> float:
		return self._k_p

	@k_p.setter
	def k_p(self, k_p: float):
		self._k_p = float(k_p)

	@property
	def k_i(self) -> float:
		return self._k_i

	@k_i.setter
	def k_i(self, k_i: float):
		self._k_i = float(k_i)

	@property
	def k_d(self) -> float:
		return self._k_d

	@k_d.setter
	def k_d(self, k_d: float):
		self._k_d = float(k_d)

	# endregion Gains
	# region States
		
	@property
	def state(self):
		return self._current_state

	@property
	def target(self) -> float:
		return self._target_state

	@target.setter
	def target(self, target: float):
		self._target_state = float(target)

	@property
	def output(self):
		return self._output

	@output.setter
	def output(self, val: float) -> float:
		"""
		Output Setter - apply limits
		"""
		if val > self.max:
			val = self.max
		elif val < self.min:
			val = self.min
		self._output = val

	@property
	def error(self) -> float:
		return self._error

	@property
	def i_error(self) -> float:
		return self._i_error

	@property
	def d_error(self) -> float:
		return self._d_error

	# endregion States
	# region Limits

	@property
	def windup_guard(self) -> float:
		return self._windup_guard

	@windup_guard.setter
	def windup_guard(self, windup_guard: float):
		if windup_guard is not None:
			self._windup_guard = float(windup_guard)
		else:
			self._windup_guard = None

	@property
	def min(self) -> float:
		return self._min

	@min.setter
	def min(self, min_val: float):
		"""
		Min Setter - force less than max
		"""
		if self.max:
			assert self.min < self.max
		if min_val is not None:
			self._min = float(min_val)
		else:
			self._min = min_val

	@property
	def max(self) -> float:
		return self._max

	@max.setter
	def max(self, max_val: float):
		"""
		Max Setter - force greater than min
		"""
		if self.min:
			assert self.min < self.max
		if max_val is not None:
			self._max = float(max_val)
		else:
			self._max = max_val

	# endregion Limits
	# region Config

	def set_config(self, config_dict: dict[str, float]):
		"""
		Set new config for PID controller
		@param config_dict: dict of PID parameters
		"""
		self.k_p = config_dict['kP']
		self.k_i = config_dict['kI']
		self.k_d = config_dict['kD']
		self.min = config_dict['min'] if config_dict['min'] != "" else None
		self.max = config_dict['max'] if config_dict['max'] != "" else None
		self.windup_guard = config_dict['windupGuard'] if config_dict['windupGuard'] != "" else None
		self.zero_i_error()

	def get_config(self) -> dict[str, float or str]:
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

	def compute(self, current_time: float, current_state: float = None) -> float:
		"""
		Compute the output of the PID controller based on the elapsed time and the current target
		@param current_time: the time at which the latest input was sampled
		@type current_time: float
		@param current_state: (Optional) current state of device PID controller is controlling. otherwise uses self._currentState
		@type current_state: float
		"""
		if not self.target:
			raise Exception("No target state set, cannot compute PID output")

		# calculate change in time
		self._delta_time = current_time - self._last_time

		# update state if available
		new_state = False
		if current_state and current_state != self._current_state:
			self._current_state = current_state
			new_state = True

		# proportional error from target
		self._error = self.target - self.state
		# integral of error from target
		self._i_error += self.error * self._delta_time

		# windup guard for integrated error
		if self.windup_guard:
			if self.i_error < -self.windup_guard:
				self._i_error = -self.windup_guard
			if self.i_error > self.windup_guard:
				self._i_error = self.windup_guard

		# derivative of error from target
		if new_state:
			# force derivative to 0 if we just changed states
			self._d_error = 0.0
		else:
			# derivative is slope of error over time
			self._d_error = (self.error - self._last_error) / self._delta_time

		# apply gains to error values
		self._output = self.k_p * self.error + self.k_i * self.i_error + self.k_d * self.d_error

		self._last_time = current_time
		self._last_error = self.error

		return self.output

	def zero_i_error(self):
		self._i_error = 0.0

	# endregion Execution

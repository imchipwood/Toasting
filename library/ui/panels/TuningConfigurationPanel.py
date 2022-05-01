import wx

from library.other.setupLogging import getLogger

from library.ui.ToastingGUIBase import ControlTuningPanelBase
from library.ui.Dialogs import error_message
from definitions import DEBUG_LEVEL


class TuningConfigurationPanel(ControlTuningPanelBase):

	# region Initialization

	def __init__(self, parent, toaster=None, timer_change_callback=None):
		"""
		Constructor for tuning config panel
		@param parent: notebook to put panel in
		@type parent: wx.Notebook
		@param toaster: State machine
		@type toaster: library.control.stateMachine.ToastStateMachine
		@param timer_change_callback: Callback to tell state machine the timer period changed
		@type timer_change_callback: func
		"""
		super().__init__(parent)
		self.toaster = toaster
		self.parent_frame = self.GetGrandParent()  # type: library.ui.ToastingGUI.ToastingGUI

		self.logger = getLogger("StateConfiguration", DEBUG_LEVEL)

		self.timer_change_callback = timer_change_callback

		# Map text ctrls to their update methods
		self._pidTextCtrlToUpdateMethodMap = {
			self.pid_p_text_ctrl: self.update_proportional_gain,
			self.pid_i_text_ctrl: self.update_integral_gain,
			self.pid_d_text_ctrl: self.update_derivative_gain,
			self.pid_min_out_limit_text_ctrl: self.update_pid_min_limit,
			self.pid_max_out_limit_text_ctrl: self.update_pid_max_limit,
			self.pid_windup_guard_text_ctrl: self.update_windup_guard,
		}
		self._otherTextCtrlToUpdateMethodMap = {
			self.timer_period_text_ctrl: self.update_timer_period,
			self.relay_pin_text_ctrl: self.update_relay_pin,
			self.spi_cs_pin_text_ctrl: self.update_thermocouple_cs_pin
		}

	def initialize_tuning_page(self):
		"""
		Initialize PID page with values from PID controller
		"""
		#
		pid = self.toaster.pid

		# Gains
		self.pid_p_text_ctrl.SetValue(str(pid.k_p))
		self.pid_i_text_ctrl.SetValue(str(pid.k_i))
		self.pid_d_text_ctrl.SetValue(str(pid.k_d))

		# Limits
		self.pid_min_out_limit_text_ctrl.SetValue(str(pid.min) if pid.min is not None else "")
		self.pid_max_out_limit_text_ctrl.SetValue(str(pid.max) if pid.max is not None else "")
		self.pid_windup_guard_text_ctrl.SetValue(str(pid.windup_guard) if pid.windup_guard is not None else "")

		# Timer period & sensor pins
		self.timer_period_text_ctrl.SetValue(str(self.timer_period))
		self.relay_pin_text_ctrl.SetValue(str(self.toaster.relay.pin))
		self.spi_cs_pin_text_ctrl.SetValue(str(self.toaster.thermocouple.csPin))

	# endregion Initialization
	# region ParentMethods

	def update_status(self, text, log_level=None):
		"""
		Interface to parent frame status update method
		@param text: text to put on status bar
		@type text: str
		@param log_level: desired logging level. Default: None (no logging)
		@type log_level: int
		"""
		self.parent_frame.update_status(text, log_level)

	# endregion ParentMethods
	# region Configuration
		# region Properties

	@property
	def timer_period(self):
		"""
		Getter for current clock timer period
		@return: current timer period
		@rtype: float
		"""
		return self.toaster.timerPeriod

	@timer_period.setter
	def timer_period(self, period_seconds):
		"""
		Setter for timer period. Reset timer on value change
		@param period_seconds: desired timer period in seconds
		@type period_seconds: float or int or str
		"""
		period_seconds = abs(float(period_seconds))
		assert period_seconds >= 0.5, "Timer period must be >= 0.5s (2Hz or less)"
		if period_seconds != self.timer_period:
			self.update_status("Timer period updated: {}".format(period_seconds))
			self.toaster.timerPeriod = period_seconds
			if self.timer_change_callback:
				self.timer_change_callback()

	@property
	def pid_config(self):
		"""
		Get the current PID config dict
		@return: dict of PIDs
		@rtype: dict[str, float]
		"""
		return self.toaster.pid.get_config()

	@pid_config.setter
	def pid_config(self, config_dict):
		"""
		Set the PID config
		@param config_dict: dict of PID values
		@type config_dict: dict[str, str]
		"""
		self.toaster.pid.set_config(config_dict)

		# endregion Properties
		# region PIDGains

	def update_proportional_gain(self):
		"""
		Update PID proportional gain from the text field
		"""
		try:
			self.pid_config = {'kP': self.pid_p_text_ctrl.GetValue()}
			self.update_status("kP updated to: {}".format(self.toaster.pid.k_p))
		except Exception as e:
			error_message(self.parent_frame, str(e), "Invalid P-Gain Value")

	def update_integral_gain(self):
		"""
		Update PID integral gain from the text field
		"""
		try:
			self.pid_config = {'kI': self.pid_i_text_ctrl.GetValue()}
			self.update_status("kI updated to: {}".format(self.toaster.pid.k_i))
		except Exception as e:
			error_message(self.parent_frame, str(e), "Invalid I-Gain Value")

	def update_derivative_gain(self):
		"""
		Update PID derivative gain from the text field
		"""
		try:
			self.pid_config = {'kD': self.pid_d_text_ctrl.GetValue()}
			self.update_status("kD updated to: {}".format(self.toaster.pid.k_d))
		except Exception as e:
			error_message(self.parent_frame, str(e), "Invalid D-Gain Value")

		# endregion PIDGains
		# region PIDLimits

	def update_pid_min_limit(self):
		"""
		Update PID output min limit from the text field
		"""
		try:
			self.pid_config = {'min': self.pid_min_out_limit_text_ctrl.GetValue()}
			self.update_status("PID min output limit updated to: {}".format(self.toaster.pid.min))
		except Exception as e:
			error_message(self.parent_frame, str(e), "Invalid PID Min Output Limit Value")

	def update_pid_max_limit(self):
		"""
		Update PID output max limit from the text field
		"""
		try:
			self.pid_config = {'max': self.pid_max_out_limit_text_ctrl.GetValue()}
			self.update_status("PID max output limit updated to: {}".format(self.toaster.pid.max))
		except Exception as e:
			error_message(self.parent_frame, str(e), "Invalid PID Max Output Limit Value")

	def update_windup_guard(self):
		"""
		Update PID windup-guard value from the text field
		"""
		try:
			self.pid_config = {'windupGuard': self.pid_windup_guard_text_ctrl.GetValue()}
			self.update_status("PID windup guard updated to: {}".format(self.toaster.pid.windup_guard))
		except Exception as e:
			error_message(self.parent_frame, str(e), "Invalid PID Windup Guard Value")

		# endregion PIDLimits
		# region GPIOPins

	def update_relay_pin(self):
		"""
		Update the relay GPIO pin # from the text field
		"""
		try:
			self.toaster.relay.pin = self.relay_pin_text_ctrl.GetValue()
		except Exception as e:
			error_message(self.parent_frame, str(e), "Invalid Relay Pin #")

	def update_thermocouple_cs_pin(self):
		"""
		Update the thermocouple chip-select pin # from the text field
		"""
		try:
			self.toaster.thermocouple.csPin = self.spi_cs_pin_text_ctrl.GetValue()
		except Exception as e:
			error_message(self.parent_frame, str(e), "Invalid SPI CS Pin #")

		# endregion GPIOPins
		# region Timer

	def update_timer_period(self):
		"""
		Update the timer period from the text field
		"""
		try:
			self.timer_period = self.timer_period_text_ctrl.GetValue()
		except:
			error_message(
				self.parent_frame,
				"Invalid value for clock timer period. Please enter a float >= 0.5 (max of 2Hz refresh)",
				"Invalid Timer Period"
			)

		# endregion Timer
		# region UpdateMethods

	def update_other_tuning_from_fields(self):
		"""
		Update various tuning variables from tuning page
		"""
		try:
			self.update_relay_pin()
			self.update_thermocouple_cs_pin()
			self.update_timer_period()
			self.update_status("Pin & Timing tuning updated")
		except Exception as e:
			error_message(self.parent_frame, str(e), "Failed to update tuning")
			raise

	def update_pid_from_fields(self):
		"""
		Update PID controller tuning from values in PID page
		"""
		try:
			self.pid_config = {
				'kP': self.pid_p_text_ctrl.GetValue(),
				'kI': self.pid_i_text_ctrl.GetValue(),
				'kD': self.pid_d_text_ctrl.GetValue(),
				'min': self.pid_min_out_limit_text_ctrl.GetValue(),
				'max': self.pid_max_out_limit_text_ctrl.GetValue(),
				'windupGuard': self.pid_windup_guard_text_ctrl.GetValue(),
			}
			self.update_status("PID tuning updated")
		except Exception as e:
			error_message(self.parent_frame, str(e), "Failed to update tuning")
			raise

	def update_all(self):
		"""
		Save the values from all fields to the data structures
		"""
		try:
			self.update_pid_from_fields()
		except:
			return
		try:
			self.update_other_tuning_from_fields()
		except:
			return
		self.update_status("All settings updated")

		# endregion UpdateMethods
	# endregion Configuration
	# region EventHandlers

	def pid_on_text_enter(self, event):
		"""
		Update PID values
		"""
		event.Skip()
		textCtrl = event.GetEventObject()
		self._pidTextCtrlToUpdateMethodMap[textCtrl]()

	def other_tuning_on_text_enter(self, event):
		"""
		Update pins/etc.
		"""
		event.Skip()
		textCtrl = event.GetEventObject()
		self._otherTextCtrlToUpdateMethodMap[textCtrl]()

	def update_all_settings_button_on_button_click(self, event):
		"""
		Event handler for update settings button - save all user-entered settings to data structures
		"""
		event.Skip()
		self.update_all()

	# endregion EventHandlers

	def __dummy(self):
		"""
		Workaround for PyCharm custom folding regions bug
		"""
		return

import wx

from library.other.setupLogging import getLogger

from library.ui.ToastingGUIBase import ControlTuningPanelBase
from library.ui.Dialogs import ErrorMessage
from definitions import DEBUG_LEVEL


class TuningConfigurationPanel(ControlTuningPanelBase):

	# region Initialization

	def __init__(self, parent, toaster=None, timerChangeCallback=None):
		"""
		Constructor for tuning config panel
		@param parent: notebook to put panel in
		@type parent: wx.Notebook
		@param toaster: State machine
		@type toaster: library.control.stateMachine.ToastStateMachine
		@param timerChangeCallback: Callback to tell state machine the timer period changed
		@type timerChangeCallback: func
		"""
		super(TuningConfigurationPanel, self).__init__(parent)
		self.toaster = toaster
		self.parentFrame = self.GetGrandParent()
		""" @type: library.ui.ToastingGUI.ToastingGUI """

		self.logger = getLogger("StateConfiguration", DEBUG_LEVEL)

		self.timerChangeCallback = timerChangeCallback

		# Map text ctrls to their update methods
		self._pidTextCtrlToUpdateMethodMap = {
			self.pidPTextCtrl: self.updateProportionalGain,
			self.pidITextCtrl: self.updateIntegralGain,
			self.pidDTextCtrl: self.updateDerivativeGain,
			self.pidMinOutLimitTextCtrl: self.updatePIDMinLimit,
			self.pidMaxOutLimitTextCtrl: self.updatePIDMaxLimit,
			self.pidWindupGuardTextCtrl: self.updateWindupGuard,
		}
		self._otherTextCtrlToUpdateMethodMap = {
			self.timerPeriodTextCtrl: self.updateTimerPeriod,
			self.relayPinTextCtrl: self.updateRelayPin,
			self.spiCsPinTextCtrl: self.updateThermocoupleCSPin
		}

	def initializeTuningPage(self):
		"""
		Initialize PID page with values from PID controller
		"""
		#
		pid = self.toaster.pid

		# Gains
		self.pidPTextCtrl.SetValue(str(pid.kP))
		self.pidITextCtrl.SetValue(str(pid.kI))
		self.pidDTextCtrl.SetValue(str(pid.kD))

		# Limits
		self.pidMinOutLimitTextCtrl.SetValue(str(pid.min) if pid.min is not None else "")
		self.pidMaxOutLimitTextCtrl.SetValue(str(pid.max) if pid.max is not None else "")
		self.pidWindupGuardTextCtrl.SetValue(str(pid.windupGuard) if pid.windupGuard is not None else "")

		# Timer period & sensor pins
		self.timerPeriodTextCtrl.SetValue(str(self.timerPeriod))
		self.relayPinTextCtrl.SetValue(str(self.toaster.relay.pin))
		self.spiCsPinTextCtrl.SetValue(str(self.toaster.thermocouple.csPin))

	# endregion Initialization
	# region ParentMethods

	def updateStatus(self, text, logLevel=None):
		"""
		Interface to parent frame status update method
		@param text: text to put on status bar
		@type text: str
		@param logLevel: desired logging level. Default: None (no logging)
		@type logLevel: int
		"""
		self.parentFrame.updateStatus(text, logLevel)

	# endregion ParentMethods
	# region Configuration
		# region Properties

	@property
	def timerPeriod(self):
		"""
		Getter for current clock timer period
		@return: current timer period
		@rtype: float
		"""
		return self.toaster.timerPeriod

	@timerPeriod.setter
	def timerPeriod(self, periodInSeconds):
		"""
		Setter for timer period. Reset timer on value change
		@param periodInSeconds: desired timer period in seconds
		@type periodInSeconds: float or int or str
		"""
		periodInSeconds = abs(float(periodInSeconds))
		assert periodInSeconds >= 0.5, "Timer period must be >= 0.5s (2Hz or less)"
		if periodInSeconds != self.timerPeriod:
			self.updateStatus("Timer period updated: {}".format(periodInSeconds))
			self.toaster.timerPeriod = periodInSeconds
			if self.timerChangeCallback:
				self.timerChangeCallback()

	@property
	def pidConfig(self):
		"""
		Get the current PID config dict
		@return: dict of PIDs
		@rtype: dict[str, float]
		"""
		return self.toaster.pid.getConfig()

	@pidConfig.setter
	def pidConfig(self, configDict):
		"""
		Set the PID config
		@param configDict: dict of PID values
		@type configDict: dict[str, str]
		"""
		self.toaster.pid.setConfig(configDict)

		# endregion Properties
		# region PIDGains

	def updateProportionalGain(self):
		"""
		Update PID proportional gain from the text field
		"""
		try:
			self.pidConfig = {'kP': self.pidPTextCtrl.GetValue()}
			self.updateStatus("kP updated to: {}".format(self.toaster.pid.kP))
		except Exception as e:
			ErrorMessage(self.parentFrame,  str(e), "Invalid P-Gain Value")

	def updateIntegralGain(self):
		"""
		Update PID integral gain from the text field
		"""
		try:
			self.pidConfig = {'kI': self.pidITextCtrl.GetValue()}
			self.updateStatus("kI updated to: {}".format(self.toaster.pid.kI))
		except Exception as e:
			ErrorMessage(self.parentFrame,  str(e), "Invalid I-Gain Value")

	def updateDerivativeGain(self):
		"""
		Update PID derivative gain from the text field
		"""
		try:
			self.pidConfig = {'kD': self.pidDTextCtrl.GetValue()}
			self.updateStatus("kD updated to: {}".format(self.toaster.pid.kD))
		except Exception as e:
			ErrorMessage(self.parentFrame,  str(e), "Invalid D-Gain Value")

		# endregion PIDGains
		# region PIDLimits

	def updatePIDMinLimit(self):
		"""
		Update PID output min limit from the text field
		"""
		try:
			self.pidConfig = {'min': self.pidMinOutLimitTextCtrl.GetValue()}
			self.updateStatus("PID min output limit updated to: {}".format(self.toaster.pid.min))
		except Exception as e:
			ErrorMessage(self.parentFrame,  str(e), "Invalid PID Min Output Limit Value")

	def updatePIDMaxLimit(self):
		"""
		Update PID output max limit from the text field
		"""
		try:
			self.pidConfig = {'max': self.pidMaxOutLimitTextCtrl.GetValue()}
			self.updateStatus("PID max output limit updated to: {}".format(self.toaster.pid.max))
		except Exception as e:
			ErrorMessage(self.parentFrame,  str(e), "Invalid PID Max Output Limit Value")

	def updateWindupGuard(self):
		"""
		Update PID windup-guard value from the text field
		"""
		try:
			self.pidConfig = {'windupGuard': self.pidWindupGuardTextCtrl.GetValue()}
			self.updateStatus("PID windup guard updated to: {}".format(self.toaster.pid.windupGuard))
		except Exception as e:
			ErrorMessage(self.parentFrame,  str(e), "Invalid PID Windup Guard Value")

		# endregion PIDLimits
		# region GPIOPins

	def updateRelayPin(self):
		"""
		Update the relay GPIO pin # from the text field
		"""
		try:
			self.toaster.relay.pin = self.relayPinTextCtrl.GetValue()
		except Exception as e:
			ErrorMessage(self.parentFrame,  str(e), "Invalid Relay Pin #")

	def updateThermocoupleCSPin(self):
		"""
		Update the thermocouple chip-select pin # from the text field
		"""
		try:
			self.toaster.thermocouple.csPin = self.spiCsPinTextCtrl.GetValue()
		except Exception as e:
			ErrorMessage(self.parentFrame,  str(e), "Invalid SPI CS Pin #")

		# endregion GPIOPins
		# region Timer

	def updateTimerPeriod(self):
		"""
		Update the timer period from the text field
		"""
		try:
			self.timerPeriod = self.timerPeriodTextCtrl.GetValue()
		except:
			ErrorMessage(
				self.parentFrame,
				"Invalid value for clock timer period. Please enter a float >= 0.5 (max of 2Hz refresh)",
				"Invalid Timer Period"
			)

		# endregion Timer
		# region UpdateMethods

	def updateOtherTuningFromFields(self):
		"""
		Update various tuning variables from tuning page
		"""
		try:
			self.updateRelayPin()
			self.updateThermocoupleCSPin()
			self.updateTimerPeriod()
			self.updateStatus("Pin & Timing tuning updated")
		except Exception as e:
			ErrorMessage(self.parentFrame,  str(e), "Failed to update tuning")
			raise

	def updatePIDsFromFields(self):
		"""
		Update PID controller tuning from values in PID page
		"""
		try:
			self.pidConfig = {
				'kP': self.pidPTextCtrl.GetValue(),
				'kI': self.pidITextCtrl.GetValue(),
				'kD': self.pidDTextCtrl.GetValue(),
				'min': self.pidMinOutLimitTextCtrl.GetValue(),
				'max': self.pidMaxOutLimitTextCtrl.GetValue(),
				'windupGuard': self.pidWindupGuardTextCtrl.GetValue(),
			}
			self.updateStatus("PID tuning updated")
		except Exception as e:
			ErrorMessage(self.parentFrame,  str(e), "Failed to update tuning")
			raise

	def updateAllSettings(self):
		"""
		Save the values from all fields to the data structures
		"""
		try:
			self.updatePIDsFromFields()
		except:
			return
		try:
			self.updateOtherTuningFromFields()
		except:
			return
		self.updateStatus("All settings updated")

		# endregion UpdateMethods
	# endregion Configuration
	# region EventHandlers

	def pidOnTextEnter(self, event):
		"""
		Update PID values
		"""
		event.Skip()
		textCtrl = event.GetEventObject()
		self._pidTextCtrlToUpdateMethodMap[textCtrl]()

	def otherTuningOnTextEnter(self, event):
		"""
		Update pins/etc.
		"""
		event.Skip()
		textCtrl = event.GetEventObject()
		self._otherTextCtrlToUpdateMethodMap[textCtrl]()

	def updateAllSettingsButtonOnButtonClick(self, event):
		"""
		Event handler for update settings button - save all user-entered settings to data structures
		"""
		event.Skip()
		self.updateAllSettings()

	# endregion EventHandlers

	def __dummy(self):
		"""
		Workaround for PyCharm custom folding regions bug
		"""
		return

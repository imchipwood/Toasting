import logging
from library.other.setupLogging import getLogger

import wx

from definitions import CONFIG_DIR

from library.other.decorators import BusyReady
from library.ui.ToastingGUIBase import ControlTuningPanelBase
from definitions import DEBUG_LEVEL


class TuningConfigurationPanel(ControlTuningPanelBase):
	def __init__(self, parent, toaster=None, timerChangeCallback=None):
		"""
		Constructor for tuning config panel
		@param parent: notebook to put panel in
		@type parent: wx.Notebook
		@param toaster: State machine
		@type toaster: library.control.stateMachine.ToastStateMachine
		"""
		super(TuningConfigurationPanel, self).__init__(parent)
		self.toaster = toaster
		self.parentFrame = self.GetGrandParent()
		""" @type: library.ui.ToastingGUI.ToastingGUI """

		self.logger = getLogger("StateConfiguration", DEBUG_LEVEL)

		self.timerChangeCallback = timerChangeCallback

		self._textCtrlToNameMap = {
			self.pidPTextCtrl: 'kP',
			self.pidITextCtrl: 'kI',
			self.pidDTextCtrl: 'kD',
			self.pidMinOutLimitTextCtrl: 'Min Limit',
			self.pidMaxOutLimitTextCtrl: 'Max Limit',
			self.pidWindupGuardTextCtrl: 'Windup Guard',
			self.timerPeriodTextCtrl: 'Timer Clock Period',
			self.relayPinTextCtrl: 'Relay GPIO Pin',
			self.spiCsPinTextCtrl: 'SPI CS Pin'
		}
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
		periodInSeconds = float(periodInSeconds)
		if periodInSeconds != self.timerPeriod:
			self.parentFrame.updateStatus("Timer period updated: {}".format(periodInSeconds))
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

	def updateProportionalGain(self):
		try:
			self.pidConfig = {'kP': self.pidPTextCtrl.GetValue()}
			self.parentFrame.updateStatus("kP updated to: {}".format(self.toaster.pid.kP))
		except Exception as e:
			self.parentFrame.errorMessage(str(e), "Invalid P-Gain Value")

	def updateIntegralGain(self):
		try:
			self.pidConfig = {'kI': self.pidITextCtrl.GetValue()}
			self.parentFrame.updateStatus("kI updated to: {}".format(self.toaster.pid.kI))
		except Exception as e:
			self.parentFrame.errorMessage(str(e), "Invalid I-Gain Value")

	def updateDerivativeGain(self):
		try:
			self.pidConfig = {'kD': self.pidDTextCtrl.GetValue()}
			self.parentFrame.updateStatus("kD updated to: {}".format(self.toaster.pid.kD))
		except Exception as e:
			self.parentFrame.errorMessage(str(e), "Invalid D-Gain Value")

	def updatePIDMinLimit(self):
		try:
			self.pidConfig = {'min': self.pidMinOutLimitTextCtrl.GetValue()}
			self.parentFrame.updateStatus("PID min output limit updated to: {}".format(self.toaster.pid.min))
		except Exception as e:
			self.parentFrame.errorMessage(str(e), "Invalid PID Min Output Limit Value")

	def updatePIDMaxLimit(self):
		try:
			self.pidConfig = {'max': self.pidMaxOutLimitTextCtrl.GetValue()}
			self.parentFrame.updateStatus("PID max output limit updated to: {}".format(self.toaster.pid.max))
		except Exception as e:
			self.parentFrame.errorMessage(str(e), "Invalid PID Max Output Limit Value")

	def updateWindupGuard(self):
		try:
			self.pidConfig = {'windupGuard': self.pidWindupGuardTextCtrl.GetValue()}
			self.parentFrame.updateStatus("PID windup guard updated to: {}".format(self.toaster.pid.windupGuard))
		except Exception as e:
			self.parentFrame.errorMessage(str(e), "Invalid PID Windup Guard Value")

	def updateRelayPin(self):
		try:
			self.toaster.relay.pin = self.relayPinTextCtrl.GetValue()
		except Exception as e:
			self.parentFrame.errorMessage(str(e), "Invalid Relay Pin #")

	def updateThermocoupleCSPin(self):
		try:
			self.toaster.thermocouple.csPin = self.spiCsPinTextCtrl.GetValue()
		except Exception as e:
			self.parentFrame.errorMessage(str(e), "Invalid SPI CS Pin #")

	def updateTimerPeriod(self):
		try:
			self.timerPeriod = self.timerPeriodTextCtrl.GetValue()
		except:
			self.parentFrame.errorMessage(
				"Invalid value for clock timer period. Please enter a float >= 0.5 (max of 2Hz refresh)",
				"Invalid Timer Period"
			)

	def updateOtherTuningFromFields(self):
		"""
		Update various tuning variables from tuning page
		"""
		try:
			self.updateRelayPin()
			self.updateThermocoupleCSPin()
			self.updateTimerPeriod()
			self.parentFrame.updateStatus("Pin & Timing tuning updated")
		except Exception as e:
			self.parentFrame.errorMessage(str(e), "Failed to update tuning")

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
			self.parentFrame.updateStatus("PID tuning updated")
		except Exception as e:
			self.parentFrame.errorMessage(str(e), "Failed to update tuning")

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
		event.Skip()
		self.updatePIDsFromFields()
		self.updateOtherTuningFromFields()
		self.parentFrame.updateStatus("All settings updated")


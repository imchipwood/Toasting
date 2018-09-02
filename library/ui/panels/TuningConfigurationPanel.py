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
		if pid.min is not None:
			self.pidMinOutLimitTextCtrl.SetValue(str(pid.min))
		if pid.max is not None:
			self.pidMaxOutLimitTextCtrl.SetValue(str(pid.max))
		if pid.windupGuard is not None:
			self.pidWindupGuardTextCtrl.SetValue(str(pid.windupGuard))

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

	def updateOtherTuning(self):
		"""
		Update various tuning variables from tuning page
		"""
		# relay pin
		try:
			self.toaster.relay.pin = int(self.relayPinTextCtrl.GetValue())
		except:
			self.parentFrame.errorMessage("Invalid pin # for relay control", "Invalid Relay Pin #")
			return

		# SPI CS pin
		try:
			self.toaster.thermocouple.csPin = int(self.spiCsPinTextCtrl.GetValue())
		except:
			self.parentFrame.errorMessage("Invalid pin # for SPI CS (enable)", "Invalid SPI CS Pin #")
			return

		try:
			self.timerPeriod = float(self.timerPeriodTextCtrl.GetValue())
		except:
			self.parentFrame.errorMessage(
				"Invalid value for clock timer period. Please enter a float >= 0.5 (max of 2Hz refresh)",
				"Invalid Timer Period"
			)
			return

	def updatePIDsFromFields(self):
		"""
		Update PID controller tuning from values in PID page
		"""
		self.pidConfig = {
			'kP': self.pidPTextCtrl.GetValue(),
			'kI': self.pidITextCtrl.GetValue(),
			'kD': self.pidDTextCtrl.GetValue(),
			'min': self.pidMinOutLimitTextCtrl.GetValue(),
			'max': self.pidMaxOutLimitTextCtrl.GetValue(),
			'windupGuard': self.pidWindupGuardTextCtrl.GetValue(),
		}

	def savePIDButtonOnButtonClick(self, event):
		"""
		Event handler for PID save button
		"""
		event.Skip()
		self.updatePIDsFromFields()
		self.parentFrame.updateStatus("PID tuning updated")

	def saveOtherTuningButtonOnButtonClick(self, event):
		"""
		Event handler for Other tuning save button
		"""
		event.Skip()
		self.updateOtherTuning()
		self.parentFrame.updateStatus("Pin & Timing tuning updated")

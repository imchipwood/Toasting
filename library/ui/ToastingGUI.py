# Generic imports
import os
import logging
from collections import OrderedDict

import matplotlib

matplotlib.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

import wx
import wx.grid

# Application imports
from library.ui.ToastingGUIBase import ToastingBase
from library.ui.panels.StateConfigurationPanel import StateConfigurationPanel
from library.ui.visualizer_liveGraph import LiveVisualizer
from library.control.stateMachine import ToastStateMachine, STATES
from library.other import decorators
from library.other.setupLogging import getLogger
from definitions import CONFIG_DIR, DATA_DIR, MODEL_NAME, DEBUG_LEVEL, CONFIG_KEY_DURATION, CONFIG_KEY_TARGET


class ToastingGUI(ToastingBase):

	# region Init

	def __init__(self, baseConfigurationPath):
		"""
		Constructor for ToastingGUI
		@param baseConfigurationPath: path to base configuration file to use
		@type baseConfigurationPath: str
		"""
		super(ToastingGUI, self).__init__(None)

		self.logger = getLogger('ToastingGUI', DEBUG_LEVEL)

		# Busy signal
		self.isBusy = True

		# Create a timer
		self.timer = wx.Timer(self)

		# Placeholder for visualizers
		self.configurationVisualizer = None
		self.liveVisualizer = None
		self.liveCanvas = None

		# Create the state machine
		self.toaster = ToastStateMachine(
			jsonConfigPath=baseConfigurationPath,
			stateMachineCompleteCallback=self.toastingComplete,
			debugLevel=DEBUG_LEVEL
		)

		# Notebook pages
		self.stateConfigPanel = StateConfigurationPanel(
			self.baseNotebook,
			self.toaster,
			# configChangeCallback=None,
			executeCallback=self.executeFromConfig
		)
		self.notebookPages = {
			'Configuration': self.stateConfigPanel,
			'Tuning': None,
			'Toasting!': None
		}
		self.pageInitFunctions = {
			'Configuration': self.stateConfigPanel.initializeConfigurationPage,
			'Tuning': self.initializeTuningPage,
			'Toasting!': self.initializeToastingPage
		}

		# state machine update
		self.testing = False
		self.testTimer = 0.0

		# status bar
		self.statusGridItems = ['relay', 'temp', 'reftemp', 'status', 'state']

		# Initialize the GUI fields
		self.initializeGuiObjects()
		
		# Bind events
		self.bindEvents()

		# Send the ready signal
		self.ready()

	def initializeGuiObjects(self):
		"""Initialize the base GUI objects"""
		# Progress bar setup
		self.progressGauge.SetRange(100)

		# Status grid
		self.setupStatusGrid()

		# Start the timer (period stored in seconds, Start() takes period in mS)
		self.timer.Start(self.timerPeriod * 1000)

		for panelName, panel in self.notebookPages.items():
			if not panel:
				continue
			if panelName == 'Configuration':
				self.baseNotebook.InsertPage(0, panel, panelName)
		self.baseNotebook.SetSelection(0)

		# Initialize all the pages
		self.updateGuiFieldsFromNewConfig()

	def bindEvents(self):
		"""Bind all events not bound in base GUI class"""
		# Busy/Ready decorators
		decorators.subscribeToBusySignal(self.busy, MODEL_NAME)
		decorators.subscribeToReadySignal(self.ready, MODEL_NAME)

		# Timer
		self.Bind(wx.EVT_TIMER, self.timerHandler)

		# close
		self.Bind(wx.EVT_CLOSE, self.onClose)

	def initCurrentPage(self):
		"""Initialize the currently selected notebook page"""
		if self.baseNotebook:
			currentPageName = self.baseNotebook.GetPageText(self.baseNotebook.GetSelection())
			# currentPageName = self.notebookPages[currentPageIndex]
			self.pageInitFunctions[currentPageName]()

	# endregion Init
	# region Properties

	@property
	def temperature(self):
		"""Getter for current temperature"""
		# if self.units == 'celsius':
		return self.toaster.temperature
		# else:
		# 	return self.convertTemp(self.toaster.temperature)

	@property
	def refTemperature(self):
		"""Getter for current reference temperature"""
		# if self.units == 'celsius':
		return self.toaster.refTemperature
		# else:
		# 	return self.convertTemp(self.toaster.refTemperature)

	@property
	def units(self):
		"""Getter for current temperature units"""
		return self.toaster.units

	@units.setter
	def units(self, units):
		"""Setter for current temperature units

		@param units: str 'fahrenheit' or 'celsius'
		"""
		self.toaster.units = units

	@property
	def stateConfiguration(self):
		"""Getter for state configuration"""
		return self.toaster.stateConfiguration

	@stateConfiguration.setter
	def stateConfiguration(self, config):
		"""Setter for state config

		@param config: state configuration
		@type config: dict
		"""
		self.toaster.stateConfiguration = config

	@property
	def timerPeriod(self):
		"""Getter for current clock timer period"""
		return self.toaster.timerPeriod

	@timerPeriod.setter
	def timerPeriod(self, periodInSeconds):
		"""Setter for timer period. Reset timer on value change

		@param periodInSeconds: desired timer period in seconds
		@type periodInSeconds: float
		"""
		# self.logger.debug("timerPeriod set: {}".format(periodInSeconds))
		if periodInSeconds != self.timerPeriod:
			self.updateStatus("Timer period updated: {}".format(periodInSeconds))
			self.timer.Stop()
			self.toaster.timerPeriod = periodInSeconds
			self.timer.Start(self.timerPeriod * 1000.0)

	@property
	def config(self):
		return self.toaster.config

	@config.setter
	def config(self, filePath):
		self.toaster.config = filePath

	@property
	def pidConfig(self):
		return self.toaster.pid.getConfig()

	@pidConfig.setter
	def pidConfig(self, configDict):
		self.toaster.pid.setConfig(configDict)

	# endregion Properties
	# region BusyReady

	def busy(self):
		"""Busy signal handler"""
		self.isBusy = True
		self.enableFields(False)
		self.progressGauge.Pulse()

	def ready(self):
		"""Ready signal handler"""
		if not self.testing:
			self.isBusy = False
			self.enableFields()
			self.progressGauge.SetValue(100)

	def enableFields(self, enable=True):
		"""Enable/Disable GUI fields

		@param enable: to enable or disable, that is the question
		@type enable: bool
		"""
		for panel in self.notebookPages.values():
			if panel:
				panel.Enable(enable)
		# self.stateConfigPanel.Enable(enable)
		# self.saveConfigButton.Enable(enable)
		# self.executeConfigButton.Enable(enable)

		# Temperature units radio boxes
		if self.toaster.running in [STATES.RUNNING, STATES.PAUSED] or self.testing:
			self.celsiusRadioButton.Enable(False)
			self.fahrenheitRadioButton.Enable(False)
		else:
			self.celsiusRadioButton.Enable(enable)
			self.fahrenheitRadioButton.Enable(enable)

		# Save data button
		try:
			if self.toaster.running not in [STATES.STOPPED, STATES.COMPLETE] or self.toaster.data == []:
				self.saveDataButton.Enable(False)
			else:
				self.saveDataButton.Enable(enable)
		except:
			self.saveDataButton.Enable(False)

		# Reflow/relay control buttons
		if self.testing:
			self.testButton.Enable(False)
			self.pauseReflowButton.Enable(False)
			self.startStopReflowButton.Enable(False)
		else:
			if self.toaster.running in [STATES.RUNNING, STATES.PAUSED]:
				self.testButton.Enable(False)
				self.pauseReflowButton.Enable(True)
				self.startStopReflowButton.Enable(True)
			else:
				self.testButton.Enable(enable)
				self.pauseReflowButton.Enable(False)
				self.startStopReflowButton.Enable(enable)

	# endregion BusyReady
	# region Visualization

	@decorators.BusyReady(MODEL_NAME)
	def redrawLiveVisualization(self):
		"""Add a new LiveVisualizer to the execution panel

		@param visualizer: matplotlib LiveVisualizer for displaying config & live data
		@type visualizer: LiveVisualizer
		"""
		sizer = self.liveVisualizationPanel.GetSizer()
		sizer.Clear()
		sizer.Layout()

		self.liveVisualizer = LiveVisualizer(stateConfiguration=self.stateConfiguration, units=self.units)
		self.liveCanvas = FigureCanvas(self.liveVisualizationPanel, -1, self.liveVisualizer.fig)
		sizer.Add(self.liveCanvas, 1, wx.EXPAND)
		self.liveVisualizationPanel.Layout()

	def updateLiveVisualization(self):
		"""Add the latest data points to the live visualization"""
		# Add data to the graph
		self.liveVisualizer.addDataPoint(
			self.toaster.timestamp,
			self.temperature,
			self.toaster.targetState,
			self.toaster.currentState
		)
		
		# Force visualizer to redraw itself with the new data
		self.liveCanvas.draw()

	# endregion Visualization
	# region Helpers

	def updateStatus(self, text, logLevel=None):
		"""Convenience function for updating status bar

		@param text: text to put on status bar
		@type text: str
		"""
		self.statusBar.SetStatusText(text)
		if logLevel == logging.INFO:
			self.logger.info(text)
		if logLevel in [logging.WARNING, logging.WARN]:
			self.logger.warning(text)
		if logLevel == logging.ERROR:
			self.logger.error(text)

	@decorators.BusyReady(MODEL_NAME)
	def temperatureUnitsChange(self):
		"""Update config/graphs/etc. when user changes units"""
		# Get the current config
		tempConfiguration = self.stateConfigPanel.convertConfigGridToStateConfig()

		# Create a new config based on the current config, but convert temps
		newConfiguration = OrderedDict()
		for state, stateDict in tempConfiguration.items():
			# start the state config
			newConfiguration[state] = {}

			# Grab values from current config
			temp = tempConfiguration[state][CONFIG_KEY_TARGET]
			duration = tempConfiguration[state][CONFIG_KEY_DURATION]

			# Update new config with converted temp
			newConfiguration[state][CONFIG_KEY_TARGET] = self.convertTemp(temp)
			newConfiguration[state][CONFIG_KEY_DURATION] = duration

		# Store updated config & redraw stuff
		self.stateConfiguration = newConfiguration

		self.initCurrentPage()

	def convertTemp(self, temp):
		"""Convert a temp to the currently set units

		@param temp: temperature value to convert
		@type temp: float
		@return: float
		"""
		if self.units == 'celsius':
			# convert fahrenheit to celsius
			return (temp - 32.0) * 5.0 / 9.0
		else:
			return temp * 9.0 / 5.0 + 32.0

	# endregion Helpers
	# region StatusGrid

	def updateStatusGrid(self):
		"""Update status grid with latest info"""
		# temps & relay
		self.updateTemperatureStatus()
		self.updateRelayStatus()

		# status
		status = STATES.TESTING if self.testing else self.toaster.running
		if status in [STATES.STOPPED, STATES.TESTING]:
			red, green, blue = 255, 100, 100
		elif status == STATES.PAUSED:
			red, green, blue = 100, 100, 255
		else:
			red, green, blue = 100, 255, 100
		self.setStatusGridCellValue('status', status)
		self.setStatusGridCellColour('status', red, green, blue)

		# state
		if self.toaster.running in [STATES.RUNNING, STATES.PAUSED]:
			stateColor = self.liveVisualizer.getColor(
				self.toaster.targetState,
				self.toaster.lastTarget
			)
			if stateColor == 'red':
				red, green, blue = 255, 100, 100
			elif stateColor == 'blue':
				red, green, blue = 100, 100, 255
			elif stateColor == 'yellow':
				red, green, blue = 255, 255, 0

			self.setStatusGridCellValue('state', self.toaster.currentState)
			self.setStatusGridCellColour('state', red, green, blue)

		elif self.toaster.running == STATES.COMPLETE:
			red, green, blue = 100, 255, 100
			self.setStatusGridCellValue('state', STATES.COMPLETE)
			self.setStatusGridCellColour('state', red, green, blue)
		else:
			red, green, blue = 255, 255, 255
			self.setStatusGridCellValue('state', '--')
			self.setStatusGridCellColour('state', red, green, blue)

	def setupStatusGrid(self):
		"""Basic setup of status grid = cell width, color, etc."""
		baseColumnWidth = 50

		# relay state
		self.statusGrid.SetCellAlignment(wx.ALIGN_CENTER, 0, 0)
		self.statusGrid.SetCellValue(0, 0, "{}".format(self.toaster.relayState))
		self.setStatusGridCellColour(statusName="relay", red=100, green=250, blue=100)
		self.statusGrid.SetColSize(0, baseColumnWidth)

		# current temperature
		self.statusGrid.SetCellAlignment(wx.ALIGN_RIGHT, 0, 1)
		self.statusGrid.SetCellValue(0, 1, "{}*".format(self.temperature))
		self.setStatusGridCellColour(statusName="temp", red=200, green=200, blue=200)
		self.statusGrid.SetColSize(1, baseColumnWidth)

		# reference temperature
		self.statusGrid.SetCellAlignment(wx.ALIGN_RIGHT, 0, 2)
		self.statusGrid.SetCellValue(0, 2, "{}*".format(self.refTemperature))
		self.setStatusGridCellColour(statusName="reftemp", red=150, green=150, blue=150)
		self.statusGrid.SetColSize(2, baseColumnWidth)

		# ready/running/complete
		self.statusGrid.SetCellAlignment(wx.ALIGN_CENTER, 0, 3)
		self.statusGrid.SetCellValue(0, 3, "Ready")
		self.setStatusGridCellColour(statusName="status", red=100, green=255, blue=100)
		self.statusGrid.SetColSize(3, baseColumnWidth+20)

		# state
		self.statusGrid.SetCellAlignment(wx.ALIGN_CENTER, 0, 4)
		self.statusGrid.SetCellValue(0, 4, "--")
		self.setStatusGridCellColour(statusName="state", red=255, green=255, blue=255)
		self.statusGrid.SetColSize(4, baseColumnWidth+30)

		# Force the sizer to adjust the layout - otherwise, grid isn't visible while GUI is initializing
		self.statusGrid.GetContainingSizer().Layout()

	def setStatusGridCellColour(self, statusName, red=0, green=0, blue=0):
		"""Updates the color of the box corresponding to the input statusName

		@param statusName: name of status grid cell to update
		@type statusName: str
		@param red: how much red
		@type red: int
		@param green: how much green
		@type red: int
		@param blue: how much blue
		@type blue: int
		"""
		col = self.statusGridItems.index(statusName)
		self.statusGrid.SetCellBackgroundColour(0, col, wx.Colour(red=red, green=green, blue=blue))
		self.statusGrid.Refresh()

	def setStatusGridCellValue(self, statusName, val):
		"""Set value of status grid cell

		@param statusName: name of status grid cell to update
		@type statusName: str
		@param val: value to set in cell
		@type val: float or str
		"""
		index = self.statusGridItems.index(statusName)

		if 'temp' in statusName:
			self.statusGrid.SetCellValue(0, index, "{:5.1f}*".format(val))
		else:
			self.statusGrid.SetCellValue(0, index, "{}".format(val))

	def updateTemperatureStatus(self):
		"""Update the status grid with the latest temperature values"""
		self.setStatusGridCellValue('temp', self.temperature)
		self.setStatusGridCellValue('reftemp', self.refTemperature)

	def updateRelayStatus(self):
		"""Update relay status grid cell based on current relay state"""
		state = self.toaster.relayState
		self.setStatusGridCellValue('relay', 'ON' if state else 'OFF')
		if state:
			red, green, blue = 255, 100, 100
		else:
			red, green, blue = 100, 255, 100
		self.setStatusGridCellColour('relay', red, green, blue)

	# endregion StatusGrid
	# region DialogHelpers

	"""Dialog helpers are simple macros for creating various wx dialog windows"""

	def infoMessage(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Info",
			style=wx.OK | wx.ICON_INFORMATION
		)
		dialog.ShowModal()
		dialog.Destroy()

	def yesNoMessage(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Toasting needs your input",
			style=wx.YES_NO | wx.ICON_INFORMATION
		)
		result = dialog.ShowModal()
		dialog.Destroy()
		return result == wx.ID_YES

	def errorMessage(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Error",
			style=wx.OK | wx.ICON_ERROR
		)
		dialog.ShowModal()
		dialog.Destroy()

	def warningMessage(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Warning",
			style=wx.OK | wx.ICON_WARNING
		)
		dialog.ShowModal()
		dialog.Destroy()

	# endregion DialogHelpers
	# region ConfigurationPage

	def executeFromConfig(self):
		"""
		Event handler for execution button
		"""
		self.baseNotebook.SetSelection(2)
		self.startStopReflowButtonOnButtonClick(None)

	def updateGuiFieldsFromNewConfig(self):
		"""Update all GUI fields pertaining to Toaster config"""
		# Units
		self.celsiusRadioButton.SetValue(self.config.units == 'celsius')
		self.fahrenheitRadioButton.SetValue(self.config.units == 'fahrenheit')

		# Configuration grid
		self.stateConfigPanel.initializeConfigurationPage()

		# Tuning page
		self.initializeTuningPage()

		# Live graph page
		self.initializeToastingPage()

	# endregion ConfigurationPage
	# region TuningPage

	def initializeTuningPage(self):
		"""Initialize PID page with values from PID controller"""
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

	def updatePIDsFromFields(self):
		"""Update PID controller tuning from values in PID page"""
		self.pidConfig = {
			'kP': self.pidPTextCtrl.GetValue(),
			'kI': self.pidITextCtrl.GetValue(),
			'kD': self.pidDTextCtrl.GetValue(),
			'min': self.pidMinOutLimitTextCtrl.GetValue(),
			'max': self.pidMaxOutLimitTextCtrl.GetValue(),
			'windupGuard': self.pidWindupGuardTextCtrl.GetValue(),
		}

	def updateOtherTuning(self):
		"""Update various tuning variables from tuning page"""
		# relay pin
		try:
			self.toaster.relay.pin = int(self.relayPinTextCtrl.GetValue())
		except:
			self.errorMessage("Invalid pin # for relay control", "Invalid Relay Pin #")
			return

		# SPI CS pin
		try:
			self.toaster.thermocouple.csPin = int(self.spiCsPinTextCtrl.GetValue())
		except:
			self.errorMessage("Invalid pin # for SPI CS (enable)", "Invalid SPI CS Pin #")
			return

		try:
			self.timerPeriod = float(self.timerPeriodTextCtrl.GetValue())
		except:
			self.errorMessage(
				"Invalid value for clock timer period. Please enter a float >= 0.5 (max of 2Hz refresh)",
				"Invalid Timer Period"
			)
			return

	def savePIDButtonOnButtonClick(self, event):
		"""Event handler for PID save button

		@param event: wx.EVT_BUTTON
		"""
		event.Skip()
		self.updatePIDsFromFields()
		self.updateStatus("PID tuning updated")

	def saveOtherTuningButtonOnButtonClick(self, event):
		"""Event handler for Other tuning save button

		@param event: wx.EVT_BUTTON
		"""
		event.Skip()
		self.updateOtherTuning()
		self.updateStatus("Pin & Timing tuning updated")

	# endregion TuningPage
	# region ToastingPage

	def initializeToastingPage(self):
		"""Draw the basic live-graph for the Toasting page"""
		self.redrawLiveVisualization()

	@decorators.BusyReady(MODEL_NAME)
	def startStopReflowButtonOnButtonClick(self, event):
		"""Event handler for start/stop reflow button

		@param event: wx.BUTTON
		"""
		if event:
			event.Skip()
		if self.startStopReflowButton.GetLabel() == 'Start Reflow':
			# re-init the page to reset the live visualization
			self.initializeToastingPage()
			self.startStopReflowButton.SetLabel('Stop Reflow')
			self.pauseReflowButton.Enable(True)
			# start reflowing
			self.toaster.start()
			self.updateStatus("Reflow process started")
		else:
			self.toaster.stop()
			self.startStopReflowButton.SetLabel('Start Reflow')
			self.pauseReflowButton.Enable(False)
			self.updateStatus("Reflow process stopped")
			self.writeDataAndConfigToDisk()
		self.pauseReflowButton.SetLabel('Pause Reflow')

	def pauseReflowButtonOnButtonClick(self, event):
		"""Event handler for pause/resume reflow button

		@param event: wx.BUTTON
		"""
		event.Skip()
		if self.pauseReflowButton.GetLabel() == "Pause Reflow":
			self.toaster.pause()
			self.pauseReflowButton.SetLabel("Resume Reflow")
			self.updateStatus("Reflow process paused")
		else:
			self.toaster.resume()
			self.pauseReflowButton.SetLabel("Pause Reflow")
			self.updateStatus("Reflow process resumed")

	def testButtonOnButtonClick(self, event):
		"""Event handler for test button

		@param event: wx.BUTTON
		"""
		event.Skip()
		self.testTimer = 0.0
		self.testing = True
		self.updateStatus("Testing relay")
		self.enableFields(False)

	@decorators.BusyReady(MODEL_NAME)
	def toastingComplete(self):
		"""Do some stuff once reflow is complete"""
		self.startStopReflowButton.SetLabel("Start Reflow")
		self.writeDataAndConfigToDisk()

	def writeDataAndConfigToDisk(self):
		"""Dump collected data to CSV"""
		dialog = wx.FileDialog(
			parent=self,
			message="Save Data & Configuration",
			defaultDir=DATA_DIR,
			defaultFile="toast_data.csv",
			style=wx.FD_SAVE
		)
		# exit if user cancelled operation
		if dialog.ShowModal() == wx.ID_CANCEL:
			self.updateStatus("Save data/config operation cancelled", logLevel=logging.WARN)
			return

		csvPath = dialog.GetPath()
		if self.toaster.dumpDataToCsv(csvPath):
			status = "CSV stored @ {}".format(csvPath)
			logLevel = None
		else:
			status = "No data to dump"
			logLevel = logging.WARN
		self.updateStatus(status, logLevel)

		# Dump config, too
		directory = os.path.dirname(csvPath)
		filename = os.path.basename(csvPath).replace(".csv", ".json")
		configPath = os.path.join(directory, filename)
		self.toaster.dumpConfig(configPath)
		status = "Config stored @ {}".format(configPath)
		self.updateStatus(status, logLevel=logging.INFO)

	# endregion ToastingPage
	# region Testing

	# @decorators.BusyReady(MODEL_NAME)
	def testTick(self):
		"""Fire this event to test relay"""
		self.setStatusGridCellValue('status', STATES.TESTING)

		# enable/disable relay at 1Hz
		if self.testTimer % 1 == 0:
			# self.logger.debug("testTimer 1Hz tick")
			if self.toaster.relayState:
				self.toaster.relay.disable()
			else:
				self.toaster.relay.enable()

		# increment test timer
		self.testTimer += self.timerPeriod

		# Are we done testing?
		if self.testTimer >= 10.0:
			# Stop testing and ensure relay is off
			self.testing = False
			self.toaster.relay.disable()
			self.updateStatus("Relay test complete")
			self.enableFields(True)

	# endregion Testing
	# region GeneralEventHandlers

	def timerHandler(self, event):
		"""Event handler for wx.Timer
		
		@param event: wx.EVT_TIMER
		"""
		event.Skip()

		# handle progress gauge
		if self.testing or self.toaster.running == STATES.RUNNING:
			self.progressGauge.Pulse()
			# disable other panels while running
			self.stateConfigPanel.Enable(False)
			self.tuningPanel.Enable(False)
		else:
			self.progressGauge.SetValue(100)
			self.stateConfigPanel.Enable(True)
			self.tuningPanel.Enable(True)

		# tell control to read thermocouple, etc.
		self.toaster.tick(self.testing)

		# check errors
		recentErrorCount = self.toaster.getRecentErrorCount()
		if recentErrorCount >= 5:
			self.toaster.stop()

			caption = "Too Many Thermocouple Errors"
			errorMessage = "There have been {} errors recently. Please check the Thermocouple connection"
			errorMessage += "\n and the thermocouple itself for issues."
			self.errorMessage(errorMessage, caption)

		# Fire test tick if we're testing the relay
		if self.testing:
			self.testTick()

		# Update live visualization if we're running
		if self.toaster.running == STATES.RUNNING:
			self.updateLiveVisualization()

		# update status grid
		self.updateStatusGrid()

	def baseNotebookOnNotebookPageChanged(self, event):
		"""Event handler for notebook page change

		@param event: wx.EVT_NOTEBOOK_PAGE_CHANGED
		"""
		event.Skip()
		self.initCurrentPage()

	def temperatureOnRadioButton(self, event):
		"""Event handler for temperature radio buttons

		@param event: wx.EVT_RADIO_BUTTON
		"""
		radioBox = event.GetEventObject()
		if radioBox == self.celsiusRadioButton and self.units == 'celsius':
			return
		elif radioBox == self.fahrenheitRadioButton and self.units == 'fahrenheit':
			return

		if radioBox == self.celsiusRadioButton:
			self.fahrenheitRadioButton.SetValue(False)
			self.units = 'celsius'
		elif radioBox == self.fahrenheitRadioButton:
			self.celsiusRadioButton.SetValue(False)
			self.units = 'fahrenheit'

		self.temperatureUnitsChange()
		self.updateTemperatureStatus()

	def saveDataButtonOnButtonClick(self, event):
		"""Event handler for save to CSV button

		@param event: wx.EVT_BUTTON
		"""
		event.Skip()
		self.writeDataAndConfigToDisk()

	def saveConfigMenuItemOnMenuSelection(self, event):
		"""Event handler for save config menu item

		@param event: wx.EVT_MENU
		"""
		event.Skip()
		self.stateConfigPanel.saveConfigDialog()

	def loadConfigMenuItemOnMenuSelection(self, event):
		"""Event handler for load config menu item

		@param event: wx.EVT_MENU
		"""
		event.Skip()
		self.stateConfigPanel.loadConfigDialog()

	def onClose(self, event):
		"""Event handler for exit

		@param event: wx.EVT_CLOSE
		"""
		event.Skip()
		self.toaster.cleanup()
		self.Destroy()
		
	# endregion GeneralEventHandlers

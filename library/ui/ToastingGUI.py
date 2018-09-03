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
from library.ui.panels.TuningConfigurationPanel import TuningConfigurationPanel
from library.ui.visualizer_liveGraph import LiveVisualizer
from library.control.stateMachine import ToastStateMachine, STATES
from library.other import decorators
from library.other.setupLogging import getLogger
from definitions import CONFIG_DIR, DATA_DIR, MODEL_NAME, DEBUG_LEVEL, CONFIG_KEY_DURATION, CONFIG_KEY_TARGET


class ToastingGUI(ToastingBase):

	RELAY_TEST_DURATION = 10.0

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
			executeCallback=self.executeFromConfig,
			configLoadCallback=self.updateGuiFieldsFromNewConfig
		)
		self.tuningConfigPanel = TuningConfigurationPanel(
			self.baseNotebook,
			self.toaster,
			timerChangeCallback=self.timerChangeCallback
		)

		self.notebookPages = OrderedDict()
		self.notebookPages['Configuration'] = self.stateConfigPanel
		self.notebookPages['Tuning'] = self.tuningConfigPanel
		self.notebookPages['Toasting!'] = None

		self.pageInitFunctions = {
			'Configuration': self.stateConfigPanel.initializeConfigurationPage,
			'Tuning': self.tuningConfigPanel.initializeTuningPage,
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
		"""
		Initialize the base GUI objects
		"""
		# Progress bar setup
		self.progressGauge.SetRange(100)

		# Status grid
		self.setupStatusGrid()

		# Start the timer (period stored in seconds, Start() takes period in mS)
		self.timer.Start(self.timerPeriod * 1000)

		for i, (panelName, panel) in enumerate(self.notebookPages.items()):
			if not panel:
				continue
			self.baseNotebook.InsertPage(i, panel, panelName)
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
		"""
		Initialize the currently selected notebook page
		"""
		if self.baseNotebook:
			currentPageName = self.baseNotebook.GetPageText(self.baseNotebook.GetSelection())
			self.pageInitFunctions[currentPageName]()

	# endregion Init
	# region Properties

	@property
	def temperature(self):
		"""
		Getter for current temperature
		@return: current temperature
		@rtype: float
		"""
		# if self.units == 'celsius':
		return self.toaster.temperature
		# else:
		# 	return self.convertTemp(self.toaster.temperature)

	@property
	def refTemperature(self):
		"""
		Getter for current reference temperature
		@return: current referencetemperature
		@rtype: float
		"""
		# if self.units == 'celsius':
		return self.toaster.refTemperature
		# else:
		# 	return self.convertTemp(self.toaster.refTemperature)

	@property
	def units(self):
		"""
		Getter for current temperature units
		@return: current units
		@rtype: str
		"""
		return self.toaster.units

	@units.setter
	def units(self, units):
		"""
		Setter for current temperature units
		@param units: str 'fahrenheit' or 'celsius'
		@type units: str
		"""
		self.toaster.units = units

	@property
	def stateConfiguration(self):
		"""
		Getter for state configuration
		@return: current state config
		@rtype: OrderedDict
		"""
		return self.toaster.stateConfiguration

	@stateConfiguration.setter
	def stateConfiguration(self, config):
		"""
		Setter for state config
		@param config: state configuration
		@type config: OrderedDict
		"""
		self.toaster.stateConfiguration = config

	@property
	def timerPeriod(self):
		"""
		Getter for current clock timer period
		@return: current clock timer period
		@rtype: float
		"""
		return self.toaster.timerPeriod

	@property
	def config(self):
		"""
		Get full config dict
		@return: full configuration dict
		@rtype: dict
		"""
		return self.toaster.config

	@config.setter
	def config(self, filePath):
		"""
		Set new config from file on disk
		@param filePath: path to config file
		@type filePath: str
		"""
		self.toaster.config = filePath

	@property
	def pidConfig(self):
		"""
		Get current PID config
		@return: pid config dict
		@rtype: dict[str, float]
		"""
		return self.toaster.pid.getConfig()

	@pidConfig.setter
	def pidConfig(self, configDict):
		"""
		Set new PID config dict
		@param configDict: PID configuration dict
		@type configDict: dict[str, float]
		"""
		self.toaster.pid.setConfig(configDict)

	# endregion Properties
	# region BusyReady

	def busy(self):
		"""
		Busy signal handler
		"""
		self.isBusy = True
		self.Enable(False)
		self.progressGauge.Pulse()

	def ready(self):
		"""
		Ready signal handler
		"""
		if not self.testing:
			self.isBusy = False
			self.Enable()
			self.progressGauge.SetValue(100)

	def Enable(self, enable=True):
		"""
		Enable/Disable GUI fields
		@param enable: to enable or disable, that is the question
		@type enable: bool
		"""
		super(ToastingGUI, self).Enable(enable)
		for panel in self.notebookPages.values():
			if panel:
				panel.Enable(enable)

		self.enableUnitsRadioBox(enable)

		self.enableControlButtons(enable)

	def enableStatusBarButtons(self, enable):
		"""
		Enable the buttons in the status bar
		@param enable: enable/disable flag
		@type enable: bool
		"""
		self.saveConfigButton.Enable(enable)
		self.loadConfigButton.Enable(enable)
		canExecute = bool(self.toaster.running not in [STATES.RUNNING, STATES.PAUSED, STATES.TESTING])
		self.executeConfigButton.Enable(enable & canExecute)

	def enableControlButtons(self, enable):
		"""
		Enable/disable the control buttons
		@param enable: enable/disable flag
		@type enable: bool
		"""
		# Save button
		try:
			if self.toaster.running not in [STATES.STOPPED, STATES.COMPLETE] or self.toaster.data == []:
				self.saveDataButton.Enable(False)
			else:
				self.saveDataButton.Enable(enable)
		except:
			self.saveDataButton.Enable(False)

		# Reflow/relay control buttons
		if self.testing:
			self.enableStatusBarButtons(False)
			self.testButton.Enable(False)
			self.pauseReflowButton.Enable(False)
			self.startStopReflowButton.Enable(False)
		else:
			if self.toaster.running in [STATES.RUNNING, STATES.PAUSED]:
				self.enableStatusBarButtons(False)
				self.testButton.Enable(False)
				self.pauseReflowButton.Enable(True)
				self.startStopReflowButton.Enable(True)
			else:
				self.enableStatusBarButtons(True)
				self.testButton.Enable(enable)
				self.pauseReflowButton.Enable(False)
				self.startStopReflowButton.Enable(enable)

	def enableUnitsRadioBox(self, enable):
		"""
		Enable the radio box in the status bar
		@param enable: enable/disable flag
		@type enable: bool
		"""
		# Temperature units radio boxes
		if self.toaster.running in [STATES.RUNNING, STATES.PAUSED] or self.testing:
			self.celsiusRadioButton.Enable(False)
			self.fahrenheitRadioButton.Enable(False)
		else:
			self.celsiusRadioButton.Enable(enable)
			self.fahrenheitRadioButton.Enable(enable)

	# endregion BusyReady
	# region Visualization

	@decorators.BusyReady(MODEL_NAME)
	def redrawLiveVisualization(self):
		"""
		Add a new LiveVisualizer to the execution panel
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
		"""
		Add the latest data points to the live visualization
		"""
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
		"""
		Convenience function for updating status bar
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
		"""
		Update config/graphs/etc. when user changes units
		"""
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
		"""
		Convert a temp to the currently set units
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
		"""
		Update status grid with latest info
		"""
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
		"""
		Basic setup of status grid = cell width, color, etc.
		"""
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
		"""
		Updates the color of the box corresponding to the input statusName
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
		"""
		Set value of status grid cell
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
		"""
		Update the status grid with the latest temperature values
		"""
		self.setStatusGridCellValue('temp', self.temperature)
		self.setStatusGridCellValue('reftemp', self.refTemperature)

	def updateRelayStatus(self):
		"""
		Update relay status grid cell based on current relay state
		"""
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
		"""
		Update all GUI fields pertaining to Toaster config
		"""
		# Units
		self.celsiusRadioButton.SetValue(self.units == 'celsius')
		self.fahrenheitRadioButton.SetValue(self.units == 'fahrenheit')

		for func in self.pageInitFunctions.values():
			func()

	# endregion ConfigurationPage
	# region TuningPage

	def timerChangeCallback(self):
		"""
		Callback from tuning page for timer period changed
		"""
		self.timer.Stop()
		self.timer.Start(self.timerPeriod * 1000.0)

	# endregion TuningPage
	# region ToastingPage

	def initializeToastingPage(self):
		"""
		Draw the basic live-graph for the Toasting page
		"""
		self.redrawLiveVisualization()

	@decorators.BusyReady(MODEL_NAME)
	def startStopReflowButtonOnButtonClick(self, event):
		"""
		Event handler for start/stop reflow button
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
		"""
		Event handler for pause/resume reflow button
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
		"""
		Event handler for test button
		"""
		event.Skip()
		self.Enable(False)
		self.updateStatus("Testing relay")
		self.testTimer = 0.0
		self.testing = True

	@decorators.BusyReady(MODEL_NAME)
	def toastingComplete(self):
		"""
		Do some stuff once reflow is complete
		"""
		self.startStopReflowButton.SetLabel("Start Reflow")
		self.writeDataAndConfigToDisk()

	def writeDataAndConfigToDisk(self):
		"""
		Dump collected data to CSV
		"""
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
		"""
		Fire this event to test relay
		"""
		self.setStatusGridCellValue('status', STATES.TESTING)

		# enable/disable relay at 1Hz
		if self.testTimer % 1 == 0:
			self.toaster.relay.toggle()
			remainingTime = self.RELAY_TEST_DURATION - self.testTimer
			self.updateStatus("Remaining relay test time: {} seconds".format(remainingTime))

		# increment test timer
		self.testTimer += self.timerPeriod

		# Stop testing and ensure relay is off after 10 seconds
		if self.testTimer >= self.RELAY_TEST_DURATION:
			self.testing = False
			self.toaster.relay.disable()
			self.updateStatus("Relay test complete")
			self.Enable(True)

	# endregion Testing
	# region SaveAndLoadConfig

	def loadConfigFromFile(self, filePath):
		"""
		Load in a new config from a JSON file path
		@param filePath: path to new JSON config file
		@type filePath: str
		"""
		self.toaster.config = filePath

		# Update the GUI
		self.updateGuiFieldsFromNewConfig()

	def loadConfigDialog(self):
		"""
		Show user a load file dialog and update configuration accordingly
		"""
		dialog = wx.FileDialog(
			parent=self,
			message="Load JSON Config File",
			defaultDir=CONFIG_DIR,
			defaultFile="toast_config.json",
			style=wx.FD_OPEN
		)

		# Do nothing if user exited dialog
		if dialog.ShowModal() == wx.ID_CANCEL:
			return

		# Extract file path from dialog and load it
		self.loadConfigFromFile(dialog.GetPath())

	@decorators.BusyReady(MODEL_NAME)
	def saveConfigDialog(self):
		"""
		Save current config to JSON file
		"""
		try:
			self.stateConfiguration = self.stateConfigPanel.convertConfigGridToStateConfig()
			self.tuningConfigPanel.updateAllSettings()
		except:
			return

		# Get the current config and use it as the target path
		currentConfigPath = self.toaster.configPath
		if currentConfigPath:
			defaultDir = os.path.dirname(currentConfigPath)
			defaultFile = os.path.basename(currentConfigPath)
		else:
			defaultDir = CONFIG_DIR
			defaultFile = "toast_config.json"

		# Create file save dialog
		dialog = wx.FileDialog(
			parent=self,
			message="Save Config to JSON File",
			defaultDir=defaultDir,
			defaultFile=defaultFile,
			style=wx.FD_SAVE
		)

		# Show dialog and return if user didn't actually choose a file
		if dialog.ShowModal() == wx.ID_CANCEL:
			self.updateStatus("Save config operation cancelled", logLevel=logging.WARN)
			return

		# Extract file path from dialog and dump config
		filePath = dialog.GetPath()
		self.toaster.dumpConfig(filePath)
		self.toaster.config = filePath
		self.updateStatus("Config saved to {}".format(self.toaster.configPath))

	# endregion SaveAndLoadConfig
	# region GeneralEventHandlers

	def saveConfigButtonOnButtonClick(self, event):
		"""
		Open the save config dialog
		"""
		event.Skip()
		self.saveConfigDialog()

	def loadConfigButtonOnButtonClick(self, event):
		"""
		Open the load config dialog
		"""
		event.Skip()
		self.loadConfigDialog()

	def executeConfigButtonOnButtonClick(self, event):
		"""
		Event handler for execution button
		"""
		event.Skip()
		self.executeFromConfig()

	def timerHandler(self, event):
		"""
		Event handler for wx.Timer
		"""
		event.Skip()

		# handle progress gauge
		if self.testing or self.toaster.running == STATES.RUNNING:
			self.progressGauge.Pulse()
			# disable other panels while running
			self.stateConfigPanel.Enable(False)
			self.tuningConfigPanel.Enable(False)
		else:
			self.progressGauge.SetValue(100)
			self.stateConfigPanel.Enable(True)
			self.tuningConfigPanel.Enable(True)

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
		"""
		Event handler for notebook page change
		"""
		event.Skip()
		self.initCurrentPage()

	def temperatureOnRadioButton(self, event):
		"""
		Event handler for temperature radio buttons
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
		"""
		Event handler for save to CSV button
		"""
		event.Skip()
		self.writeDataAndConfigToDisk()

	def saveConfigMenuItemOnMenuSelection(self, event):
		"""
		Event handler for save config menu item
		"""
		event.Skip()
		self.saveConfigDialog()

	def loadConfigMenuItemOnMenuSelection(self, event):
		"""
		Event handler for load config menu item
		"""
		event.Skip()
		self.loadConfigDialog()

	def aboutMenuItemOnMenuSelection(self, event):
		"""
		Event handler for about menu item
		"""
		event.Skip()
		self.infoMessage(message="See https://www.github.com/imchipwood/Toasting for more info", caption="About")

	def onClose(self, event):
		"""
		Event handler for exit
		"""
		event.Skip()
		self.toaster.cleanup()
		self.Destroy()
		
		# endregion GeneralEventHandlers

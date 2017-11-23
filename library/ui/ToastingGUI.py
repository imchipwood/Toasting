import json
import logging
import os
from collections import OrderedDict

import matplotlib

matplotlib.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

import wx
import wx.grid

from library.ui.ToastingGUIBase import ToastingBase
from library.ui.visualizer_configuration import ConfigurationVisualizer, CONFIG_KEY_DURATION, CONFIG_KEY_TARGET
from library.ui.visualizer_liveGraph import LiveVisualizer
from library.control.stateMachine import ToastStateMachine
from library.other import decorators
from library.other.setupLogging import getLogger
from definitions import CONFIG_DIR, DATA_DIR

MODEL_NAME = "Toasting"

DEBUG_LEVEL = logging.INFO
DEBUG_LEVEL = logging.DEBUG


class ToastingGUI(ToastingBase):

	# region Init

	def __init__(self, parent):
		ToastingBase.__init__(self, parent)

		self.logger = getLogger('ToastingGUI', DEBUG_LEVEL)

		# Busy signal
		self.isBusy = True

		# Create a timer
		self.timer = wx.Timer(self)

		# Placeholder for visualizers
		self.configurationVisualizer = None
		self.liveVisualizer = None
		self.liveCanvas = None

		# Get initial configuration from testconfig.json
		baseConfigPath = os.path.join(CONFIG_DIR, "testconfig.json")
		self.config = self.getConfigFromJsonFile(baseConfigPath)
		pins = self.config['pins']
		tuning = self.config['tuning']
		self._units = self.config['units']

		# Create a state machine with an empty configuration dict
		self.toaster = ToastStateMachine(
			stateConfiguration=self.config['states'],
			timerPeriod=tuning['timerPeriod'],
			csPin=pins['SPI_CS'],
			relayPin=pins['relay'],
			stateMachineCompleteCallback=self.toastingComplete,
			pidTuning=tuning['pid'],
			debugLevel=DEBUG_LEVEL
		)
		self.timerPeriod = tuning['timerPeriod']

		# set this after creating control
		self.stateConfiguration = self.config['states']

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

		self.updateGuiFromJsonConfig(self.config)

	def bindEvents(self):
		"""Bind all events not bound in base GUI class"""
		# Busy/Ready decorators
		decorators.subscribeToBusySignal(self.busy, MODEL_NAME)
		decorators.subscribeToReadySignal(self.ready, MODEL_NAME)

		# Grid events
		self.configurationGrid.Bind(
			wx.grid.EVT_GRID_CELL_CHANGED,
			self.configurationGridOnGridCellChange
		)

		# Timer
		self.Bind(wx.EVT_TIMER, self.timerHandler)

		# close
		self.Bind(wx.EVT_CLOSE, self.onClose)

	@decorators.BusyReady(MODEL_NAME)
	def setupConfigurationGrid(self, configDict):
		"""Set up the configuration grid with

		@param configDict: dict of config steps
		@type configDict: dict
		"""
		# clear out all columns and rows
		if self.configurationGrid.GetNumberCols():
			self.configurationGrid.DeleteCols(0, self.configurationGrid.GetNumberCols())
			self.configurationGrid.DeleteRows(0, self.configurationGrid.GetNumberRows())

		# Set up the rows
		self.configurationGrid.AppendRows(2)
		self.configurationGrid.SetRowLabelValue(0, "Target Temp")
		self.configurationGrid.SetRowLabelValue(1, "Step Duration")

		# Set up the columns and insert the values from the config dict
		for colNum, stepName in enumerate(configDict.keys()):
			# Add a column
			self.configurationGrid.AppendCols(1)
			# Set column label (step name)
			self.configurationGrid.SetColLabelValue(colNum, stepName)
			# Insert config values
			targetTemp = str(configDict[stepName][CONFIG_KEY_TARGET])
			stepDuration = str(configDict[stepName][CONFIG_KEY_DURATION])
			self.configurationGrid.SetCellValue(col=colNum, row=0, s=targetTemp)
			self.configurationGrid.SetCellValue(col=colNum, row=1, s=stepDuration)

	def initializeExecutionPage(self):
		"""Initialize the execution page with a new config"""
		# get current config
		self.stateConfiguration = self.convertConfigGridToStateConfig()

		# Initialize live visualizer
		self.liveVisualizer = LiveVisualizer(stateConfiguration=self.stateConfiguration, units=self.units)
		self.redrawLiveVisualization(visualizer=self.liveVisualizer)

	def initializePIDPage(self):
		"""Initialize PID page with values from PID controller"""
		pid = self.toaster.pid
		# self.logger.debug("initializePIDPage P, I, D: {}, {}, {}".format(pid.kP, pid.kI, pid.kD))
		self.pidPTextCtrl.SetValue(str(pid.kP))
		self.pidITextCtrl.SetValue(str(pid.kI))
		self.pidDTextCtrl.SetValue(str(pid.kD))
		if pid.min is not None:
			self.pidMinOutLimitTextCtrl.SetValue(str(pid.min))
		if pid.max is not None:
			self.pidMaxOutLimitTextCtrl.SetValue(str(pid.max))
		if pid.maxIError is not None:
			self.pidIErrorLimitTextCtrl.SetValue(str(pid.maxIError))

		self.timerPeriodTextCtrl.SetValue(str(self.timerPeriod))
		self.relayPinTextCtrl.SetValue(str(self.toaster.relay.pin))
		self.spiCsPinTextCtrl.SetValue(str(self.toaster.thermocouple.csPin))

	def updatePIDsFromFields(self):
		"""Update PID controller tuning from values in PID page"""
		self.logger.debug("updatePIDsFromFields")
		kP = self.pidPTextCtrl.GetValue()
		if kP is "":
			kP = 0.0
		self.toaster.pid.kP = float(kP)
		kI = self.pidITextCtrl.GetValue()
		if kI is "":
			kI = 0.0
		self.toaster.pid.kI = float(kI)
		kD = self.pidDTextCtrl.GetValue()
		if kD is "":
			kD = 0.0
		self.toaster.pid.kD = float(kD)

		minVal = self.pidMinOutLimitTextCtrl.GetValue()
		if minVal is not u"":
			self.toaster.pid.min = float(minVal)
		maxVal = self.pidMaxOutLimitTextCtrl.GetValue()
		if maxVal is not u"":
			self.toaster.pid.max = float(maxVal)
		maxIError = self.pidIErrorLimitTextCtrl.GetValue()
		if maxIError is not u"":
			self.toaster.pid.maxIError = float(maxIError)

	def updateOtherTuning(self):
		"""Update various tuning variables from tuning page"""
		# relay pin
		try:
			relayPin = int(self.relayPinTextCtrl.GetValue())
		except:
			self.errorMessage("Invalid pin # for relay control", "Invalid Relay Pin #")
			return
		if relayPin != self.toaster.relay.pin:
			self.toaster.relay.pin = relayPin

		# SPI CS pin
		try:
			spiCsPin = int(self.spiCsPinTextCtrl.GetValue())
		except:
			self.errorMessage("Invalid pin # for SPI CS (enable)", "Invalid SPI CS Pin #")
			return
		if spiCsPin != self.toaster.thermocouple.csPin:
			self.toaster.thermocouple.csPin = spiCsPin

		try:
			period = float(self.timerPeriodTextCtrl.GetValue())
		except:
			self.errorMessage(
				"Invalid value for clock timer period. Please enter a float >= 0.5 (max of 2Hz refresh)",
				"Invalid Timer Period"
			)
			return

		# Reset timer
		self.timerPeriod = period

	# endregion Init
	# region Properties

	@property
	def temperature(self):
		"""Getter for current temperature"""
		if self.units == 'celcius':
			return self.toaster.temperature
		else:
			return self.convertTemp(self.toaster.temperature)

	@property
	def refTemperature(self):
		"""Getter for current reference temperature"""
		if self.units == 'celcius':
			return self.toaster.refTemperature
		else:
			return self.convertTemp(self.toaster.refTemperature)

	@property
	def units(self):
		"""Getter for current temperature units"""
		return self.config['units']

	@units.setter
	def units(self, units):
		"""Setter for current temperature units

		@param units: str 'fahrenheit' or 'celcius'
		"""
		self.config['units'] = units

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
		self.baseNotebook.Enable(enable)
		self.configurationGrid.Enable(enable)
		self.saveConfigButton.Enable(enable)
		self.executeConfigButton.Enable(enable)

		# Temperature units radio boxes
		if self.toaster.running in ['Running', 'Paused'] or self.testing:
			self.celciusRadioButton.Enable(False)
			self.fahrenheitRadioButton.Enable(False)
		else:
			self.celciusRadioButton.Enable(enable)
			self.fahrenheitRadioButton.Enable(enable)

		# Save data button
		try:
			if self.toaster.running not in ['Stopped', 'Complete'] or self.toaster.data == []:
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
			if self.toaster.running in ['Running', 'Paused']:
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
	def redrawConfigurationVisualization(self, visualizer):
		"""Add a new configurationVisualizer to the configuration panel

		@param visualizer: matplotlib configurationVisualizer for displaying config setup
		@type visualizer: ConfigurationVisualizer
		"""
		# Clear out existing configurationVisualizer
		sizer = self.configurationVisualizerPanel.GetSizer()
		sizer.Clear()
		sizer.Layout()

		# Create and add the configurationVisualizer canvas to the sizer
		canvas = FigureCanvas(self.configurationVisualizerPanel, -1, visualizer.fig)
		sizer.Add(canvas, 1, wx.EXPAND)
		self.configurationVisualizerPanel.Layout()

	@decorators.BusyReady(MODEL_NAME)
	def redrawLiveVisualization(self, visualizer):
		"""Add a new LiveVisualizer to the execution panel

		@param visualizer: matplotlib LiveVisualizer for displaying config & live data
		@type visualizer: LiveVisualizer
		"""
		sizer = self.liveVisualizationPanel.GetSizer()
		sizer.Clear()
		sizer.Layout()

		self.liveCanvas = FigureCanvas(self.liveVisualizationPanel, -1, visualizer.fig)
		sizer.Add(self.liveCanvas, 1, wx.EXPAND)
		self.liveVisualizationPanel.Layout()

	def updateLiveVisualization(self):
		"""Add the latest data points to the live visualization"""
		self.liveVisualizer.addDataPoint(
			self.toaster.timestamp,
			self.temperature,
			self.toaster.target,
			self.toaster.currentState
		)
		self.liveCanvas.draw()

	# endregion Visualization
	# region Helpers

	def toastingComplete(self):
		"""Do some stuff once reflow is complete"""
		self.dumpToCsv()

	def updateStatus(self, text):
		"""Convenience function for updating status bar

		@param text: text to put on status bar
		@type text: str
		"""
		self.statusBar.SetStatusText(text)

	def temperatureUnitsChange(self):
		"""Update config/graphs/etc. when user changes units"""
		# Get the current config
		tempConfiguration = self.convertConfigGridToStateConfig()

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
		self.updateConfigurationGrid()

	def convertTemp(self, temp):
		"""Convert a temp to the currently set units

		@param temp: temperature value to convert
		@type temp: float
		@return: float
		"""
		if self.units == 'celcius':
			# convert fahrenheit to celcius
			return (temp - 32.0) * 5.0 / 9.0
		else:
			return temp * 9.0 / 5.0 + 32.0

	def updateStatusGrid(self):
		"""Update status grid with latest info"""
		# temps & relay
		self.updateTemperatureStatus()
		self.updateRelayStatus()

		# status
		status = 'Testing' if self.testing else self.toaster.running
		if status in ['Stopped', 'Testing']:
			red, green, blue = 255, 100, 100
		elif status == 'Paused':
			red, green, blue = 100, 100, 255
		else:
			red, green, blue = 100, 255, 100
		self.setStatusGridCellValue('status', status)
		self.setStatusGridCellColour('status', red, green, blue)

		# state
		if self.toaster.running in ['Running', 'Paused']:
			stateColor = self.liveVisualizer.getColor(
				self.toaster.target,
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

		elif self.toaster.running == 'Complete':
			red, green, blue = 100, 255, 100
			self.setStatusGridCellValue('state', 'Complete')
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
		# self.statusGrid.Layout()
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

	def dumpToCsv(self):
		"""Dump collected data to CSV"""
		dialog = wx.FileDialog(
			parent=self,
			message="Save Data To CSV",
			defaultDir=DATA_DIR,
			defaultFile="toast_data.csv",
			style=wx.FD_SAVE
		)
		# exit if user cancelled operation
		if dialog.ShowModal() == wx.CANCEL:
			return

		csvPath = dialog.GetPath()
		if self.toaster.dumpDataToCsv(csvPath):
			self.updateStatus("CSV stored @ {}".format(csvPath))
		else:
			self.updateStatus("No data to dump")

	def infoMessage(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Warning",
			style=wx.OK | wx.ICON_INFORMATION
		)
		dialog.ShowModal()
		dialog.Destroy()

	def yesNoMessage(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Warning",
			style=wx.YES_NO | wx.ICON_INFORMATION
		)
		result = dialog.ShowModal()
		dialog.Destroy()
		return result == wx.ID_YES

	def errorMessage(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Warning",
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

	# endregion Helpers
	# region Config

	def getConfigFromJsonFile(self, jsonFile):
		"""Get config from a JSON file

		@param jsonFile: file path
		@type jsonFile: str
		@return: OrderedDict
		"""
		with open(jsonFile) as inf:
			return json.load(inf, object_pairs_hook=OrderedDict)

	@decorators.BusyReady(MODEL_NAME)
	def saveConfig(self):
		"""Save current config to JSON file"""
		# Create file save dialog
		dialog = wx.FileDialog(
			parent=self,
			message="Save Config to JSON File",
			defaultDir=CONFIG_DIR,
			defaultFile="toast_config.json",
			style=wx.FD_SAVE
		)

		# Show dialog and return if user didn't actually choose a file
		if dialog.ShowModal() == wx.ID_CANCEL:
			return

		# Extract file path from dialog and dump config
		filePath = dialog.GetPath()
		with open(filePath, 'w') as oup:
			config = OrderedDict()
			config['units'] = self.units
			config['pins'] = {}
			config['pins']['SPI_CS'] = self.toaster.thermocouple.csPin
			config['pins']['relay'] = self.toaster.relay.pin
			config['tuning'] = {}
			config['tuning']['timerPeriod'] = self.timerPeriod
			config['tuning']['pid'] = self.toaster.pid.getConfig()
			config['states'] = self.convertConfigGridToStateConfig()
			json.dump(config, oup, indent=4)
			self.updateStatus("Config saved to {}".format(filePath))

	def loadConfigFromFile(self, filePath):

		self.config = self.getConfigFromJsonFile(filePath)
		self.stateConfiguration = self.config['states']

		# Update the GUI
		self.updateGuiFromJsonConfig(self.config)

	def loadConfigDialog(self):
		"""Show user a load file dialog and update configuration accordingly"""
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

	def updateConfigurationGrid(self):
		"""Update the grid and visualization with new configuration"""
		# Update config grid
		self.setupConfigurationGrid(self.stateConfiguration)

		# Create new configurationVisualizer and draw it
		self.configurationVisualizer = ConfigurationVisualizer(self.stateConfiguration, units=self.units)
		self.redrawConfigurationVisualization(self.configurationVisualizer)
		self.updateStatus("Configuration Updated")

	def getStateConfigurationFromJsonFile(self, configPath):
		"""Parse a JSON config file and return the states specifically

		@param configPath: path to configuration json file
		@type configPath: str
		@return: OrderedDict
		"""
		config = self.getConfigFromJsonFile(configPath)
		return config['states']

	def updateGuiFromJsonConfig(self, config):
		"""Call any time a new JSON config is read

		@param config: full toast config
		@type config: dict
		"""
		# Configuration grid
		self.updateConfigurationGrid()

		# Units
		self.units = config['units']
		self.celciusRadioButton.SetValue(self.units == 'celcius')
		self.fahrenheitRadioButton.SetValue(self.units == 'fahrenheit')

		# Tuning
		tuning = config['tuning']
		self.updatePIDFromConfigDict(tuning['pid'])
		self.timerPeriod = tuning['timerPeriod']

		# Pin #s
		pins = config['pins']
		self.toaster.relay.pin = pins['relay']
		self.toaster.thermocouple.pin = pins['SPI_CS']

	def updatePIDFromConfigDict(self, pidConfig):
		"""Update the PID controller tuning

		@param pidConfig: PID configuration
		@type pidConfig: dict
		"""
		# self.logger.debug("updatePIDFromConfigDict")
		# self.logger.debug(json.dumps(pidConfig, indent=2))
		self.toaster.pid.kP = pidConfig['kP']
		self.toaster.pid.kI = pidConfig['kI']
		self.toaster.pid.kD = pidConfig['kD']
		if pidConfig['min'] != "":
			self.toaster.pid.min = pidConfig['min']
		if pidConfig['max'] != "":
			self.toaster.pid.max = pidConfig['max']
		if pidConfig['maxierror'] != "":
			self.toaster.pid.maxierror = pidConfig['maxierror']
		self.updateStatus("PIDs Updated")

	def convertConfigGridToStateConfig(self):
		"""Put values from grid into dictionary

		@return: OrderedDict
		"""
		configDict = OrderedDict()

		# Loop over columns
		for colNum in range(0, self.configurationGrid.GetNumberCols()):
			# Get step name and associated values
			stepName = self.configurationGrid.GetColLabelValue(col=colNum)
			targetTemp = self.configurationGrid.GetCellValue(col=colNum, row=0)
			stepDuration = self.configurationGrid.GetCellValue(col=colNum, row=1)

			# add step to dict
			configDict[stepName] = {
				CONFIG_KEY_TARGET: float(targetTemp),
				CONFIG_KEY_DURATION: int(stepDuration)
			}

		return configDict

	# endregion Config
	# region Testing

	@decorators.BusyReady(MODEL_NAME)
	def testTick(self):
		"""Fire this event to test relay"""
		self.setStatusGridCellValue('status', 'Testing')

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

	# endregion Testing
	# region EventHandlers

	def timerHandler(self, event):
		"""Event handler for wx.Timer
		
		@param event: wx.EVT_TIMER
		"""
		event.Skip()

		# handle progress gauge
		if self.testing or self.toaster.running == 'Running':
			self.progressGauge.Pulse()
		else:
			self.progressGauge.SetValue(100)

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
		if self.toaster.running == 'Running':
			self.updateLiveVisualization()

		# update status grid
		self.updateStatusGrid()

	@decorators.BusyReady(MODEL_NAME)
	def startStopReflowButtonOnButtonClick(self, event):
		"""Event handler for start/stop reflow button

		@param event: wx.BUTTON
		"""
		event.Skip()
		if self.startStopReflowButton.GetLabel() == 'Start Reflow':
			# re-init the page to reset the live visualization
			self.initializeExecutionPage()
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

	# @decorators.BusyReady(MODEL_NAME)
	def testButtonOnButtonClick(self, event):
		"""Event handler for test button

		@param event: wx.BUTTON
		"""
		event.Skip()
		self.testTimer = 0.0
		self.testing = True
		self.updateStatus("Testing relay")

	def executeConfigButtonOnButtonClick(self, event):
		"""Event handler for execution button

		@param event: wx.EVT_BUTTON
		"""
		event.Skip()
		self.baseNotebook.SetSelection(2)

	def baseNotebookOnNotebookPageChanged(self, event):
		"""Event handler for notebook page change

		@param event: wx.EVT_NOTEBOOK_PAGE_CHANGED
		"""
		event.Skip()
		index = event.GetEventObject().GetSelection()
		if index == 0:
			# do nothing - leave existing config alone
			return
		elif index == 1:
			self.initializePIDPage()
		elif index == 2:
			self.initializeExecutionPage()

	def savePIDButtonOnButtonClick(self, event):
		"""Event handler for PID save button

		@param event: wx.EVT_BUTTON
		"""
		event.Skip()
		self.updatePIDsFromFields()

	def saveOtherTuningButtonOnButtonClick(self, event):
		"""Event handler for Other tuning save button

		@param event: wx.EVT_BUTTON
		"""
		event.Skip()
		self.updateOtherTuning()

	@decorators.BusyReady(MODEL_NAME)
	def configurationGridOnGridCellChange(self, event):
		"""Event handler for cell value changing

		@param event: wx.grid.EVT_GRID_CELL_CHANGED
		"""
		event.Skip()
		self.stateConfiguration = self.convertConfigGridToStateConfig()
		self.configurationVisualizer = ConfigurationVisualizer(self.stateConfiguration)
		self.redrawConfigurationVisualization(self.configurationVisualizer)

	@decorators.BusyReady(MODEL_NAME)
	def temperatureOnRadioButton(self, event):
		"""Event handler for temperature radio buttons

		@param event: wx.EVT_RADIO_BUTTON
		"""
		# self.logger.debug("temperatureOnRadioButton")
		radioBox = event.GetEventObject()
		if radioBox == self.celciusRadioButton and self.units == 'celcius':
			return
		elif radioBox == self.fahrenheitRadioButton and self.units == 'fahrenheit':
			return

		if radioBox == self.celciusRadioButton:
			self.fahrenheitRadioButton.SetValue(False)
			self.units = 'celcius'
		elif radioBox == self.fahrenheitRadioButton:
			self.celciusRadioButton.SetValue(False)
			self.units = 'fahrenheit'

		self.temperatureUnitsChange()
		self.updateTemperatureStatus()

	def saveDataButtonOnButtonClick(self, event):
		"""Event handler for save to CSV button

		@param event: wx.EVT_BUTTON
		"""
		event.Skip()
		self.dumpToCsv()

	def saveConfigButtonOnButtonClick(self, event):
		"""Event handler for save config button

		@param event: wx.EVT_BUTTON
		"""
		event.Skip()
		self.saveConfig()

	def loadConfigButtonOnButtonClick(self, event):
		"""Event handler for load config button

		@param event: wx.EVT_BUTTON
		"""
		event.Skip()
		self.loadConfigDialog()

	def saveConfigMenuItemOnMenuSelection(self, event):
		"""Event handler for save config menu item

		@param event: wx.EVT_MENU
		"""
		event.Skip()
		self.saveConfig()

	def loadConfigMenuItemOnMenuSelection(self, event):
		"""Event handler for load config menu item

		@param event: wx.EVT_MENU
		"""
		event.Skip()
		self.loadConfigDialog()

	def onClose(self, event):
		"""Event handler for exit

		@param event: wx.EVT_CLOSE
		"""
		event.Skip()
		self.toaster.cleanup()
		self.Destroy()
		
	# endregion EventHandlers


if __name__ == '__main__':
	# create the base app
	app = wx.App()

	# instantiate the view
	view = ToastingGUI(None)
	view.Show()

	# bring the view to the top & run it
	app.SetTopWindow(view)
	app.MainLoop()

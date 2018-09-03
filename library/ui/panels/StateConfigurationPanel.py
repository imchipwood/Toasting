import os
import logging
from collections import OrderedDict
import matplotlib

from library.other.setupLogging import getLogger

matplotlib.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import wx
import wx.grid

from definitions import CONFIG_DIR
from library.other.decorators import BusyReady
from library.ui.ToastingGUIBase import StateConfigurationPanelBase
from definitions import CONFIG_KEY_DURATION, CONFIG_KEY_TARGET, DEBUG_LEVEL, MODEL_NAME
from library.ui.visualizer_configuration import ConfigurationVisualizer


class StateConfigurationPanel(StateConfigurationPanelBase):

	# region Initialization

	def __init__(self, parent, toaster=None, executeCallback=None, configLoadCallback=None):
		"""
		Constructor for state config panel
		@param parent: notebook to put panel in
		@type parent: wx.Notebook
		@param toaster: State machine
		@type toaster: library.control.stateMachine.ToastStateMachine
		@param executeCallback: callback for the execute button
		@type executeCallback: function
		"""
		super(StateConfigurationPanel, self).__init__(parent)
		self.toaster = toaster
		self.parentFrame = self.GetGrandParent()
		""" @type: library.ui.ToastingGUI.ToastingGUI """

		self.logger = getLogger("StateConfiguration", DEBUG_LEVEL)

		self.configurationVisualizer = None

		# Callbacks
		self.executeCallback = executeCallback
		self.configLoadCallback = configLoadCallback

		# Grid events
		self.configurationGrid.Bind(
			wx.grid.EVT_GRID_CELL_CHANGED,
			self.configurationGridOnGridCellChange
		)

		self.initializeConfigurationPage()

	def Enable(self, enable=True):
		"""
		Enable/disable this panel & all of its widgets
		@param enable: enable/disable flag
		@type enable: bool
		"""
		super(StateConfigurationPanel, self).Enable(enable)
		self.saveConfigButton.Enable(enable)
		self.loadConfigButton.Enable(enable)
		self.executeConfigButton.Enable(enable)
		self.configurationGrid.Enable(enable)

	@BusyReady(MODEL_NAME)
	def initializeConfigurationPage(self):
		"""
		Set up the configuration grid based on current state config
		"""
		self.configurationGrid.Freeze()

		# clear out all columns
		if self.configurationGrid.GetNumberCols():
			self.configurationGrid.DeleteCols(0, self.configurationGrid.GetNumberCols())

		# Set up the columns and insert the values from the config dict
		self._initGridColumns()

		self.configurationGrid.Thaw()

		self.redrawConfigurationVisualization()

	def _initGridColumns(self):
		"""
		Add a column for each step
		"""
		for colNum, (stepName, stepDict) in enumerate(self.stateConfiguration.items()):
			# Add a column
			self.configurationGrid.AppendCols(1)

			# Set column label (step name)
			self.configurationGrid.SetColLabelValue(colNum, stepName)
			self.configurationGrid.SetColSize(colNum, 100)

			# Insert config values
			targetTemp = str(stepDict.get(CONFIG_KEY_TARGET, ""))
			stepDuration = str(stepDict.get(CONFIG_KEY_DURATION, ""))
			self.configurationGrid.SetCellValue(0, colNum, targetTemp)
			self.configurationGrid.SetCellValue(1, colNum, stepDuration)

			# Set cell alignment to center
			for rowNum in range(self.configurationGrid.GetNumberRows()):
				self.configurationGrid.SetCellAlignment(wx.ALIGN_CENTER, rowNum, colNum)

	def updateGuiFieldsFromNewConfig(self):
		"""
		Update all GUI fields pertaining to Toaster config
		"""
		self.initializeConfigurationPage()
		if self.configLoadCallback:
			self.configLoadCallback()

	def convertConfigGridToStateConfig(self):
		"""
		Put values from grid into dictionary
		@rtype: OrderedDict
		"""
		configDict = OrderedDict()

		# Loop over columns
		for colNum in range(self.configurationGrid.GetNumberCols()):
			# Get step name and associated values
			stepName = self.configurationGrid.GetColLabelValue(colNum)
			targetTemp = self.configurationGrid.GetCellValue(0, colNum)
			stepDuration = self.configurationGrid.GetCellValue(1, colNum)

			# add step to dict
			configDict[stepName] = {
				CONFIG_KEY_TARGET: float(targetTemp),
				CONFIG_KEY_DURATION: int(stepDuration)
			}

		return configDict

	# endregion Initialization
	# region Properties

	@property
	def stateConfiguration(self):
		if self.toaster:
			return self.toaster.stateConfiguration
		else:
			return {}

	@stateConfiguration.setter
	def stateConfiguration(self, configDict):
		self.toaster.stateConfiguration = configDict

	@property
	def units(self):
		return self.toaster.units

	# endregion Properties
	# region Visualization

	# @decorators.BusyReady(MODEL_NAME)
	def redrawConfigurationVisualization(self):
		"""
		Add a new configurationVisualizer to the configuration panel
		"""
		# Clear out existing configurationVisualizer
		sizer = self.configurationVisualizerPanel.GetSizer()
		sizer.Clear()
		sizer.Layout()

		# Create and add the configurationVisualizer canvas to the sizer
		visualizer = ConfigurationVisualizer(self.stateConfiguration, units=self.units)
		canvas = FigureCanvas(self.configurationVisualizerPanel, -1, visualizer.fig)
		sizer.Add(canvas, 1, wx.EXPAND)
		self.configurationVisualizerPanel.Layout()

	# endregion Visualization
	# region EventHandlers
		# region Buttons

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
		if self.executeCallback:
			self.executeCallback()

		# endregion Buttons
		# region Grid

	@BusyReady(MODEL_NAME)
	def configurationGridOnGridCellChange(self, event):
		"""
		Redraw the reflow profile visualization when a value in the grid changes
		"""
		event.Skip()
		self.stateConfiguration = self.convertConfigGridToStateConfig()
		self.redrawConfigurationVisualization()

		# endregion Grid
	# endregion EventHandlers
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

	@BusyReady(MODEL_NAME)
	def saveConfigDialog(self):
		"""
		Save current config to JSON file
		"""

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
			self.parentFrame.updateStatus("Save config operation cancelled", logLevel=logging.WARN)
			return

		# Extract file path from dialog and dump config
		filePath = dialog.GetPath()
		self.toaster.dumpConfig(filePath)
		self.toaster.configPath = filePath
		self.parentFrame.updateStatus("Config saved to {}".format(filePath))

		# endregion SaveAndLoadConfig


if __name__ == "__main__":
	app = wx.App()

	from library.control.stateMachine import ToastStateMachine
	toaster = ToastStateMachine()

	from library.ui.ToastingGUIBase import PanelTestFrame
	view = PanelTestFrame(None)

	sizer = view.GetSizer()

	panel = StateConfigurationPanel(parent=view, toaster=toaster)
	sizer.Add(panel, 1, wx.EXPAND)
	view.Layout()

	view.Show()
	app.SetTopWindow(view)
	app.MainLoop()

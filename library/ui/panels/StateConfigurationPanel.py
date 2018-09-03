import os
import logging
from collections import OrderedDict
import matplotlib

from library.other.setupLogging import getLogger

matplotlib.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import wx
import wx.grid

from library.other.decorators import BusyReady
from library.ui.ToastingGUIBase import StateConfigurationPanelBase
from definitions import CONFIG_KEY_DURATION, CONFIG_KEY_TARGET, DEBUG_LEVEL, MODEL_NAME
from library.ui.visualizer_configuration import ConfigurationVisualizer


class GRIDINFO:
	ROW_NAME = 0
	ROW_TARGET = 1
	ROW_DURATION = 2


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
			self.configurationGrid.SetColSize(colNum, 100)

			# Insert config values
			targetTemp = str(stepDict.get(CONFIG_KEY_TARGET, ""))
			stepDuration = str(stepDict.get(CONFIG_KEY_DURATION, ""))
			self.configurationGrid.SetCellValue(GRIDINFO.ROW_NAME, colNum, stepName)
			self.configurationGrid.SetCellValue(GRIDINFO.ROW_TARGET, colNum, targetTemp)
			self.configurationGrid.SetCellValue(GRIDINFO.ROW_DURATION, colNum, stepDuration)

			# Set cell alignment to center
			for rowNum in range(self.configurationGrid.GetNumberRows()):
				self.configurationGrid.SetCellAlignment(wx.ALIGN_CENTER, rowNum, colNum)

	def convertConfigGridToStateConfig(self):
		"""
		Put values from grid into dictionary
		@rtype: OrderedDict
		"""
		configDict = OrderedDict()

		# Loop over columns
		for colNum in range(self.configurationGrid.GetNumberCols()):
			# Get step name and associated values
			stepName = self.configurationGrid.GetCellValue(GRIDINFO.ROW_NAME, colNum)
			targetTemp = self.configurationGrid.GetCellValue(GRIDINFO.ROW_TARGET, colNum)
			stepDuration = self.configurationGrid.GetCellValue(GRIDINFO.ROW_DURATION, colNum)

			if "" in [stepName, targetTemp, stepDuration]:
				raise Exception("Column '{}' is missing data. Cancelling operation.".format(colNum))

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

	def addStepButtonOnButtonClick(self, event):
		"""
		Add a column to the grid
		"""
		event.Skip()
		self.configurationGrid.AppendCols(1)
		colNum = self.configurationGrid.GetNumberCols() - 1
		self.configurationGrid.SetColSize(colNum, 100)
		for rowNum in range(self.configurationGrid.GetNumberRows()):
			self.configurationGrid.SetCellAlignment(wx.ALIGN_CENTER, rowNum, colNum)

	def removeStepButtonOnButtonClick(self, event):
		"""
		Remove a column from the grid
		"""
		event.Skip()
		self.configurationGrid.DeleteCols(self.configurationGrid.GetNumberCols() - 1, 1)
		self.configurationGridOnGridCellChange(None)

		# endregion Buttons
		# region Grid

	@BusyReady(MODEL_NAME)
	def configurationGridOnGridCellChange(self, event):
		"""
		Redraw the reflow profile visualization when a value in the grid changes
		"""
		if event:
			event.Skip()
		try:
			self.stateConfiguration = self.convertConfigGridToStateConfig()
			self.redrawConfigurationVisualization()
		except Exception as e:
			self.logger.debug("Failed to update config - ignoring.\n{}".format(e))
			pass

		# endregion Grid
		# endregion EventHandlers


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

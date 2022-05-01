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

	def __init__(self, parent, toaster=None, execute_callback=None, config_load_callback=None):
		"""
		Constructor for state config panel
		@param parent: notebook to put panel in
		@type parent: wx.Notebook
		@param toaster: State machine
		@type toaster: library.control.stateMachine.ToastStateMachine
		@param execute_callback: callback for the execute button
		@type execute_callback: function
		"""
		super().__init__(parent)
		self.toaster = toaster
		self.parentFrame = self.GetGrandParent()  # type: library.ui.ToastingGUI.ToastingGUI

		self.logger = getLogger("StateConfiguration", DEBUG_LEVEL)

		self.configuration_visualizer = None

		# Callbacks
		self.execute_callback = execute_callback
		self.config_load_callback = config_load_callback

		# Grid events
		self.configuration_grid.Bind(
			wx.grid.EVT_GRID_CELL_CHANGED,
			self.configuration_grid_on_grid_cell_change
		)

		self.initialize_configuration_page()

	def Enable(self, enable=True):
		"""
		Enable/disable this panel & all of its widgets
		@param enable: enable/disable flag
		@type enable: bool
		"""
		super(StateConfigurationPanel, self).Enable(enable)
		self.configuration_grid.Enable(enable)

	@BusyReady(MODEL_NAME)
	def initialize_configuration_page(self):
		"""
		Set up the configuration grid based on current state config
		"""
		self.configuration_grid.Freeze()

		# clear out all columns
		if self.configuration_grid.GetNumberCols():
			self.configuration_grid.DeleteCols(0, self.configuration_grid.GetNumberCols())

		# Set up the columns and insert the values from the config dict
		self._init_grid_columns()

		self.configuration_grid.Thaw()

		self.redraw_configuration_visualization()

	def _init_grid_columns(self):
		"""
		Add a column for each step
		"""
		for col_num, (step_name, step_dict) in enumerate(self.state_configuration.items()):
			# Add a column
			self.configuration_grid.AppendCols(1)
			self.configuration_grid.SetColSize(col_num, 100)

			# Insert config values
			target_temp = str(step_dict.get(CONFIG_KEY_TARGET, ""))
			step_duration = str(step_dict.get(CONFIG_KEY_DURATION, ""))
			self.configuration_grid.SetCellValue(GRIDINFO.ROW_NAME, col_num, step_name)
			self.configuration_grid.SetCellValue(GRIDINFO.ROW_TARGET, col_num, target_temp)
			self.configuration_grid.SetCellValue(GRIDINFO.ROW_DURATION, col_num, step_duration)

			# Set cell alignment to center
			for row_num in range(self.configuration_grid.GetNumberRows()):
				self.configuration_grid.SetCellAlignment(row_num, col_num, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

	def convert_config_grid_to_state_config(self):
		"""
		Put values from grid into dictionary
		@rtype: OrderedDict
		"""
		config_dict = OrderedDict()

		# Loop over columns
		for col_num in range(self.configuration_grid.GetNumberCols()):
			# Get step name and associated values
			step_name = self.configuration_grid.GetCellValue(GRIDINFO.ROW_NAME, col_num)
			target_temp = self.configuration_grid.GetCellValue(GRIDINFO.ROW_TARGET, col_num)
			step_duration = self.configuration_grid.GetCellValue(GRIDINFO.ROW_DURATION, col_num)

			if "" in [step_name, target_temp, step_duration]:
				raise Exception("Column '{}' is missing data. Cancelling operation.".format(col_num))

			# add step to dict
			config_dict[step_name] = {
				CONFIG_KEY_TARGET: float(target_temp),
				CONFIG_KEY_DURATION: int(step_duration)
			}

		return config_dict

	# endregion Initialization
	# region Properties

	@property
	def state_configuration(self):
		if self.toaster:
			return self.toaster.state_configuration
		else:
			return {}

	@state_configuration.setter
	def state_configuration(self, config_dict):
		self.toaster.state_configuration = config_dict

	@property
	def units(self):
		return self.toaster.units

	# endregion Properties
	# region Visualization

	def redraw_configuration_visualization(self):
		"""
		Add a new configurationVisualizer to the configuration panel
		"""
		# Clear out existing configurationVisualizer
		sizer = self.configuration_visualizer_panel.GetSizer()
		sizer.Clear()
		sizer.Layout()

		# Create and add the configurationVisualizer canvas to the sizer
		visualizer = ConfigurationVisualizer(self.state_configuration, units=self.units)
		canvas = FigureCanvas(self.configuration_visualizer_panel, -1, visualizer.fig)
		sizer.Add(canvas, 1, wx.EXPAND)
		self.configuration_visualizer_panel.Layout()

	# endregion Visualization
	# region EventHandlers
		# region Buttons

	def add_step_button_on_button_click(self, event):
		"""
		Add a column to the grid
		"""
		event.Skip()
		self.configuration_grid.AppendCols(1)
		col_num = self.configuration_grid.GetNumberCols() - 1
		self.configuration_grid.SetColSize(col_num, 100)
		for rowNum in range(self.configuration_grid.GetNumberRows()):
			self.configuration_grid.SetCellAlignment(rowNum, col_num, wx.ALIGN_CENTER, wx.ALIGN_CENTER)

	def remove_step_button_on_button_click(self, event):
		"""
		Remove a column from the grid
		"""
		event.Skip()
		self.configuration_grid.DeleteCols(self.configuration_grid.GetNumberCols() - 1, 1)
		self.configuration_grid_on_grid_cell_change(None)

		# endregion Buttons
		# region Grid

	@BusyReady(MODEL_NAME)
	def configuration_grid_on_grid_cell_change(self, event):
		"""
		Redraw the reflow profile visualization when a value in the grid changes
		"""
		if event:
			event.Skip()
		try:
			self.state_configuration = self.convert_config_grid_to_state_config()
			self.redraw_configuration_visualization()
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

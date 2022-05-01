# Generic imports
import logging
import os
from collections import OrderedDict

import matplotlib

matplotlib.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

import wx
import wx.grid

# Application imports
from library.ui.ToastingGUIBase import ToastingBase
from library.ui.Dialogs import info_message, error_message
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

	def __init__(self, base_configuration_path):
		"""
		Constructor for ToastingGUI
		@param base_configuration_path: path to base configuration file to use
		@type base_configuration_path: str
		"""
		super(ToastingGUI, self).__init__(None)

		self.logger = getLogger('ToastingGUI', DEBUG_LEVEL)

		# Busy signal
		self.is_busy = True

		# Create a timer
		self.timer = wx.Timer(self)

		# Placeholder for visualizers
		self.configuration_visualizer = None
		self.live_visualizer = None
		self.live_canvas = None

		# Create the state machine
		self.toaster = ToastStateMachine(
			jsonConfigPath=base_configuration_path,
			stateMachineCompleteCallback=self.toasting_complete,
			debugLevel=DEBUG_LEVEL
		)

		# Notebook pages
		self.state_config_panel = StateConfigurationPanel(
			self.base_notebook,
			self.toaster,
			execute_callback=self.execute_from_config,
			config_load_callback=self.update_gui_files_from_new_config
		)
		self.tuning_config_panel = TuningConfigurationPanel(
			self.base_notebook,
			self.toaster,
			timer_change_callback=self.timer_change_callback
		)

		self.notebook_pages = OrderedDict()
		self.notebook_pages['Configuration'] = self.state_config_panel
		self.notebook_pages['Tuning'] = self.tuning_config_panel
		self.notebook_pages['Toasting!'] = None

		self.pageInitFunctions = {
			'Configuration': self.state_config_panel.initialize_configuration_page,
			'Tuning': self.tuning_config_panel.initialize_tuning_page,
			'Toasting!': self.initialize_toasting_page
		}

		# state machine update
		self.testing = False
		self.testTimer = 0.0

		# status bar
		self.status_grid_items = ['relay', 'temp', 'reftemp', 'status', 'state']

		# Initialize the GUI fields
		self.initialize_gui_objects()
		
		# Bind events
		self.bind_events()

		# Send the ready signal
		self.ready()

	def initialize_gui_objects(self):
		"""
		Initialize the base GUI objects
		"""
		# Progress bar setup
		self.progress_gauge.SetRange(100)

		# Status grid
		self.setup_status_grid()

		# Start the timer (period stored in seconds, Start() takes period in mS)
		self.timer.Start(self.timerPeriod * 1000)

		for i, (panelName, panel) in enumerate(self.notebook_pages.items()):
			if not panel:
				continue
			self.base_notebook.InsertPage(i, panel, panelName)
		self.base_notebook.SetSelection(0)

		# Initialize all the pages
		self.update_gui_files_from_new_config()

	def bind_events(self):
		"""Bind all events not bound in base GUI class"""
		# Busy/Ready decorators
		decorators.subscribeToBusySignal(self.busy, MODEL_NAME)
		decorators.subscribeToReadySignal(self.ready, MODEL_NAME)

		# Timer
		self.Bind(wx.EVT_TIMER, self.timer_handler)

		# close
		self.Bind(wx.EVT_CLOSE, self.on_close)

	def init_current_page(self):
		"""
		Initialize the currently selected notebook page
		"""
		if self.base_notebook:
			current_page_name = self.base_notebook.GetPageText(self.base_notebook.GetSelection())
			self.pageInitFunctions[current_page_name]()

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
	def ref_temperature(self):
		"""
		Getter for current reference temperature
		@return: current referencetemperature
		@rtype: float
		"""
		# if self.units == 'celsius':
		return self.toaster.ref_temperature
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
	def state_configuration(self):
		"""
		Getter for state configuration
		@return: current state config
		@rtype: OrderedDict
		"""
		return self.toaster.state_configuration

	@state_configuration.setter
	def state_configuration(self, config):
		"""
		Setter for state config
		@param config: state configuration
		@type config: OrderedDict
		"""
		self.toaster.state_configuration = config

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
	def config(self, file_path):
		"""
		Set new config from file on disk
		@param file_path: path to config file
		@type file_path: str
		"""
		self.toaster.config = file_path

	@property
	def pid_config(self):
		"""
		Get current PID config
		@return: pid config dict
		@rtype: dict[str, float]
		"""
		return self.toaster.pid.get_config()

	@pid_config.setter
	def pid_config(self, config_dict):
		"""
		Set new PID config dict
		@param config_dict: PID configuration dict
		@type config_dict: dict[str, float]
		"""
		self.toaster.pid.set_config(config_dict)

	# endregion Properties
	# region BusyReady

	def busy(self):
		"""
		Busy signal handler
		"""
		self.is_busy = True
		self.Enable(False)
		self.progress_gauge.Pulse()

	def ready(self):
		"""
		Ready signal handler
		"""
		if not self.testing:
			self.is_busy = False
			self.Enable()
			self.progress_gauge.SetValue(100)

	def Enable(self, enable=True):
		"""
		Enable/Disable GUI fields
		@param enable: to enable or disable, that is the question
		@type enable: bool
		"""
		super().Enable(enable)
		for panel in self.notebook_pages.values():
			if panel:
				panel.Enable(enable)

		self.enable_units_radio_box(enable)

		self.enable_control_buttons(enable)

	def enable_status_bar_buttons(self, enable):
		"""
		Enable the buttons in the status bar
		@param enable: enable/disable flag
		@type enable: bool
		"""
		self.save_config_button.Enable(enable)
		self.load_config_button.Enable(enable)
		canExecute = bool(self.toaster.running not in [STATES.RUNNING, STATES.PAUSED, STATES.TESTING])
		self.execute_config_button.Enable(enable & canExecute)

	def enable_control_buttons(self, enable):
		"""
		Enable/disable the control buttons
		@param enable: enable/disable flag
		@type enable: bool
		"""
		# Save button
		try:
			if self.toaster.running not in [STATES.STOPPED, STATES.COMPLETE] or self.toaster.data == []:
				self.save_data_button.Enable(False)
			else:
				self.save_data_button.Enable(enable)
		except:
			self.save_data_button.Enable(False)

		# Reflow/relay control buttons
		if self.testing:
			self.enable_status_bar_buttons(False)
			self.test_button.Enable(False)
			self.pause_reflow_button.Enable(False)
			self.start_stop_reflow_button.Enable(False)
		else:
			if self.toaster.running in [STATES.RUNNING, STATES.PAUSED]:
				self.enable_status_bar_buttons(False)
				self.test_button.Enable(False)
				self.pause_reflow_button.Enable(True)
				self.start_stop_reflow_button.Enable(True)
			else:
				self.enable_status_bar_buttons(True)
				self.test_button.Enable(enable)
				self.pause_reflow_button.Enable(False)
				self.start_stop_reflow_button.Enable(enable)

	def enable_units_radio_box(self, enable):
		"""
		Enable the radio box in the status bar
		@param enable: enable/disable flag
		@type enable: bool
		"""
		# Temperature units radio boxes
		if self.toaster.running in [STATES.RUNNING, STATES.PAUSED] or self.testing:
			self.celsius_radio_button.Enable(False)
			self.fahrenheit_radio_button.Enable(False)
		else:
			self.celsius_radio_button.Enable(enable)
			self.fahrenheit_radio_button.Enable(enable)

	# endregion BusyReady
	# region Visualization

	@decorators.BusyReady(MODEL_NAME)
	def redraw_live_visualization(self):
		"""
		Add a new LiveVisualizer to the execution panel
		"""
		sizer = self.live_visualization_panel.GetSizer()
		sizer.Clear()
		sizer.Layout()

		self.live_visualizer = LiveVisualizer(state_configuration=self.state_configuration, units=self.units)
		self.live_canvas = FigureCanvas(self.live_visualization_panel, -1, self.live_visualizer.fig)
		sizer.Add(self.live_canvas, 1, wx.EXPAND)
		self.live_visualization_panel.Layout()

	def update_live_visualization(self):
		"""
		Add the latest data points to the live visualization
		"""
		# Add data to the graph
		self.live_visualizer.add_data_point(
			self.toaster.timestamp,
			self.temperature,
			self.toaster.targetState,
			self.toaster.currentState
		)
		
		# Force visualizer to redraw itself with the new data
		self.live_canvas.draw()

	# endregion Visualization
	# region Helpers

	def update_status(self, text, logLevel=None):
		"""
		Convenience function for updating status bar
		@param text: text to put on status bar
		@type text: str
		@param logLevel: desired logging level. Default: None (no logging)
		@type logLevel: int
		"""
		self.status_bar.SetStatusText(text)
		if logLevel is not None:
			if logLevel in [logging.WARNING, logging.WARN]:
				self.logger.warning(text)
			elif logLevel == logging.ERROR:
				self.logger.error(text)
			else:
				self.logger.info(text)

	@decorators.BusyReady(MODEL_NAME)
	def temperature_units_change(self):
		"""
		Update config/graphs/etc. when user changes units
		"""
		# Get the current config
		temp_configuration = self.state_config_panel.convert_config_grid_to_state_config()

		# Create a new config based on the current config, but convert temps
		new_configuration = OrderedDict()
		for state, stateDict in temp_configuration.items():
			# start the state config
			new_configuration[state] = {}

			# Grab values from current config
			temp = temp_configuration[state][CONFIG_KEY_TARGET]
			duration = temp_configuration[state][CONFIG_KEY_DURATION]

			# Update new config with converted temp
			new_configuration[state][CONFIG_KEY_TARGET] = self.convert_temperature(temp)
			new_configuration[state][CONFIG_KEY_DURATION] = duration

		# Store updated config & redraw stuff
		self.state_configuration = new_configuration

		self.init_current_page()

	def convert_temperature(self, temp):
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

	def update_status_grid(self):
		"""
		Update status grid with latest info
		"""
		# temps & relay
		self.update_temperature_status()
		self.update_relay_status()

		# status
		status = STATES.TESTING if self.testing else self.toaster.running
		if status in [STATES.STOPPED, STATES.TESTING]:
			red, green, blue = 255, 100, 100
		elif status == STATES.PAUSED:
			red, green, blue = 100, 100, 255
		else:
			red, green, blue = 100, 255, 100
		self.set_status_grid_cell_value('status', status)
		self.set_status_grid_cell_color('status', red, green, blue)

		# state
		if self.toaster.running in [STATES.RUNNING, STATES.PAUSED]:
			state_color = self.live_visualizer.getColor(
				self.toaster.targetState,
				self.toaster.lastTarget
			)
			if state_color == 'red':
				red, green, blue = 255, 100, 100
			elif state_color == 'blue':
				red, green, blue = 100, 100, 255
			elif state_color == 'yellow':
				red, green, blue = 255, 255, 0

			self.set_status_grid_cell_value('state', self.toaster.currentState)
			self.set_status_grid_cell_color('state', red, green, blue)

		elif self.toaster.running == STATES.COMPLETE:
			red, green, blue = 100, 255, 100
			self.set_status_grid_cell_value('state', STATES.COMPLETE)
			self.set_status_grid_cell_color('state', red, green, blue)
		else:
			red, green, blue = 255, 255, 255
			self.set_status_grid_cell_value('state', '--')
			self.set_status_grid_cell_color('state', red, green, blue)

	def setup_status_grid(self):
		"""
		Basic setup of status grid = cell width, color, etc.
		"""
		base_column_width = 50

		# relay state
		self.status_grid.SetCellAlignment(0, 0, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.status_grid.SetCellValue(0, 0, "{}".format(self.toaster.relayState))
		self.set_status_grid_cell_color(statusName="relay", red=100, green=250, blue=100)
		self.status_grid.SetColSize(0, base_column_width)

		# current temperature
		self.status_grid.SetCellAlignment(0, 1, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
		self.status_grid.SetCellValue(0, 1, "{}*".format(self.temperature))
		self.set_status_grid_cell_color(statusName="temp", red=200, green=200, blue=200)
		self.status_grid.SetColSize(1, base_column_width)

		# reference temperature
		self.status_grid.SetCellAlignment(0, 2, wx.ALIGN_RIGHT, wx.ALIGN_CENTER)
		self.status_grid.SetCellValue(0, 2, "{}*".format(self.ref_temperature))
		self.set_status_grid_cell_color(statusName="reftemp", red=150, green=150, blue=150)
		self.status_grid.SetColSize(2, base_column_width)

		# ready/running/complete
		self.status_grid.SetCellAlignment(0, 3, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.status_grid.SetCellValue(0, 3, "Ready")
		self.set_status_grid_cell_color(statusName="status", red=100, green=255, blue=100)
		self.status_grid.SetColSize(3, base_column_width+20)

		# state
		self.status_grid.SetCellAlignment(0, 4, wx.ALIGN_CENTER, wx.ALIGN_CENTER)
		self.status_grid.SetCellValue(0, 4, "--")
		self.set_status_grid_cell_color(statusName="state", red=255, green=255, blue=255)
		self.status_grid.SetColSize(4, base_column_width+30)

		# Force the sizer to adjust the layout - otherwise, grid isn't visible while GUI is initializing
		self.status_grid.GetContainingSizer().Layout()

	def set_status_grid_cell_color(self, statusName, red=0, green=0, blue=0):
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
		col = self.status_grid_items.index(statusName)
		self.status_grid.SetCellBackgroundColour(0, col, wx.Colour(red=red, green=green, blue=blue))
		self.status_grid.Refresh()

	def set_status_grid_cell_value(self, statusName, val):
		"""
		Set value of status grid cell
		@param statusName: name of status grid cell to update
		@type statusName: str
		@param val: value to set in cell
		@type val: float or str
		"""
		index = self.status_grid_items.index(statusName)

		if 'temp' in statusName:
			self.status_grid.SetCellValue(0, index, "{:5.1f}*".format(val))
		else:
			self.status_grid.SetCellValue(0, index, "{}".format(val))

	def update_temperature_status(self):
		"""
		Update the status grid with the latest temperature values
		"""
		self.set_status_grid_cell_value('temp', self.temperature)
		self.set_status_grid_cell_value('reftemp', self.ref_temperature)

	def update_relay_status(self):
		"""
		Update relay status grid cell based on current relay state
		"""
		state = self.toaster.relayState
		self.set_status_grid_cell_value('relay', 'ON' if state else 'OFF')
		if state:
			red, green, blue = 255, 100, 100
		else:
			red, green, blue = 100, 255, 100
		self.set_status_grid_cell_color('relay', red, green, blue)

	# endregion StatusGrid
	# region DialogHelpers

	"""Dialog helpers are simple macros for creating various wx dialog windows"""

	def info_message(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Info",
			style=wx.OK | wx.ICON_INFORMATION
		)
		dialog.ShowModal()
		dialog.Destroy()

	def yes_no_message(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Toasting needs your attention!",
			style=wx.YES_NO | wx.ICON_INFORMATION
		)
		result = dialog.ShowModal()
		dialog.Destroy()
		return result == wx.ID_YES

	def error_message(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Error!",
			style=wx.OK | wx.ICON_ERROR
		)
		dialog.ShowModal()
		dialog.Destroy()

	def warning_message(self, message, caption=None):
		dialog = wx.MessageDialog(
			parent=self,
			message=message,
			caption=caption if caption else "Warning!",
			style=wx.OK | wx.ICON_WARNING
		)
		dialog.ShowModal()
		dialog.Destroy()

	# endregion DialogHelpers
	# region ConfigurationPage

	def execute_from_config(self):
		"""
		Event handler for execution button
		"""
		self.base_notebook.SetSelection(2)
		self.start_stop_reflow_button_on_button_click(None)

	def update_gui_files_from_new_config(self):
		"""
		Update all GUI fields pertaining to Toaster config
		"""
		# Units
		self.celsius_radio_button.SetValue(self.units == 'celsius')
		self.fahrenheit_radio_button.SetValue(self.units == 'fahrenheit')

		for func in self.pageInitFunctions.values():
			func()

	# endregion ConfigurationPage
	# region TuningPage

	def timer_change_callback(self):
		"""
		Callback from tuning page for timer period changed
		"""
		self.timer.Stop()
		self.timer.Start(self.timerPeriod * 1000.0)

	# endregion TuningPage
	# region ToastingPage

	def initialize_toasting_page(self):
		"""
		Draw the basic live-graph for the Toasting page
		"""
		self.redraw_live_visualization()

	@decorators.BusyReady(MODEL_NAME)
	def start_stop_reflow_button_on_button_click(self, event):
		"""
		Event handler for start/stop reflow button
		"""
		if event:
			event.Skip()
		if self.start_stop_reflow_button.GetLabel() == 'Start Reflow':
			# re-init the page to reset the live visualization
			self.initialize_toasting_page()
			self.start_stop_reflow_button.SetLabel('Stop Reflow')
			self.pause_reflow_button.Enable(True)
			# start reflowing
			self.toaster.start()
			self.update_status("Reflow process started")
		else:
			self.toaster.stop()
			self.start_stop_reflow_button.SetLabel('Start Reflow')
			self.pause_reflow_button.Enable(False)
			self.update_status("Reflow process stopped")
			self.write_data_and_config_to_disk()
		self.pause_reflow_button.SetLabel('Pause Reflow')

	def pause_reflow_button_on_button_click(self, event):
		"""
		Event handler for pause/resume reflow button
		"""
		event.Skip()
		if self.pause_reflow_button.GetLabel() == "Pause Reflow":
			self.toaster.pause()
			self.pause_reflow_button.SetLabel("Resume Reflow")
			self.update_status("Reflow process paused")
		else:
			self.toaster.resume()
			self.pause_reflow_button.SetLabel("Pause Reflow")
			self.update_status("Reflow process resumed")

	def test_button_on_button_click(self, event):
		"""
		Event handler for test button
		"""
		event.Skip()
		self.Enable(False)
		self.update_status("Testing relay")
		self.testTimer = 0.0
		self.testing = True

	@decorators.BusyReady(MODEL_NAME)
	def toasting_complete(self):
		"""
		Do some stuff once reflow is complete
		"""
		self.start_stop_reflow_button.SetLabel("Start Reflow")
		self.write_data_and_config_to_disk()

	def write_data_and_config_to_disk(self):
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
			self.update_status("Save data/config operation cancelled", logLevel=logging.WARN)
			return

		csvPath = dialog.GetPath()
		if self.toaster.dumpDataToCsv(csvPath):
			status = "CSV stored @ {}".format(csvPath)
			logLevel = None
		else:
			status = "No data to dump"
			logLevel = logging.WARN
		self.update_status(status, logLevel)

		# Dump config, too
		directory = os.path.dirname(csvPath)
		filename = os.path.basename(csvPath).replace(".csv", ".json")
		configPath = os.path.join(directory, filename)
		self.toaster.dumpConfig(configPath)
		status = "Config stored @ {}".format(configPath)
		self.update_status(status, logLevel=logging.INFO)

	# endregion ToastingPage
	# region Testing

	# @decorators.BusyReady(MODEL_NAME)
	def test_tick(self):
		"""
		Fire this event to test relay
		"""
		self.set_status_grid_cell_value('status', STATES.TESTING)

		# enable/disable relay at 1Hz
		if self.testTimer % 1 == 0:
			self.toaster.relay.toggle()
			remainingTime = self.RELAY_TEST_DURATION - self.testTimer
			self.update_status("Remaining relay test time: {} seconds".format(remainingTime))

		# increment test timer
		self.testTimer += self.timerPeriod

		# Stop testing and ensure relay is off after 10 seconds
		if self.testTimer >= self.RELAY_TEST_DURATION:
			self.testing = False
			self.toaster.relay.disable()
			self.update_status("Relay test complete")
			self.Enable(True)

	# endregion Testing
	# region SaveAndLoadConfig

	def load_config_from_file(self, filePath):
		"""
		Load in a new config from a JSON file path
		@param filePath: path to new JSON config file
		@type filePath: str
		"""
		self.toaster.config = filePath

		# Update the GUI
		self.update_gui_files_from_new_config()

	def load_config_dialog(self):
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
		self.load_config_from_file(dialog.GetPath())

	@decorators.BusyReady(MODEL_NAME)
	def save_config_dialog(self):
		"""
		Save current config to JSON file
		"""
		try:
			self.state_configuration = self.state_config_panel.convert_config_grid_to_state_config()
			self.tuning_config_panel.update_all()
		except:
			return

		# Get the current config and use it as the target path
		current_config_path = self.toaster.configPath
		if current_config_path:
			default_dir = os.path.dirname(current_config_path)
			default_file = os.path.basename(current_config_path)
		else:
			default_dir = CONFIG_DIR
			default_file = "toast_config.json"

		# Create file save dialog
		dialog = wx.FileDialog(
			parent=self,
			message="Save Config to JSON File",
			defaultDir=default_dir,
			defaultFile=default_file,
			style=wx.FD_SAVE
		)

		# Show dialog and return if user didn't actually choose a file
		if dialog.ShowModal() == wx.ID_CANCEL:
			self.update_status("Save config operation cancelled", logLevel=logging.WARN)
			return

		# Extract file path from dialog and dump config
		file_path = dialog.GetPath()
		self.toaster.dumpConfig(file_path)
		self.toaster.config = file_path
		self.update_status("Config saved to {}".format(self.toaster.configPath))

	# endregion SaveAndLoadConfig
	# region GeneralEventHandlers

	def save_config_button_on_button_click(self, event):
		"""
		Open the save config dialog
		"""
		event.Skip()
		self.save_config_dialog()

	def load_config_button_on_button_click(self, event):
		"""
		Open the load config dialog
		"""
		event.Skip()
		self.load_config_dialog()

	def execute_config_button_on_button_click(self, event):
		"""
		Event handler for execution button
		"""
		event.Skip()
		self.execute_from_config()

	def timer_handler(self, event):
		"""
		Event handler for wx.Timer
		"""
		event.Skip()

		# handle progress gauge
		if self.testing or self.toaster.running == STATES.RUNNING:
			self.progress_gauge.Pulse()
			# disable other panels while running
			self.state_config_panel.Enable(False)
			self.tuning_config_panel.Enable(False)
		else:
			self.progress_gauge.SetValue(100)
			self.state_config_panel.Enable(True)
			self.tuning_config_panel.Enable(True)

		# tell control to read thermocouple, etc.
		self.toaster.tick(self.testing)

		# check errors
		recent_error_count = self.toaster.getRecentErrorCount()
		if recent_error_count >= 5:
			self.toaster.stop()

			caption = "Too Many Thermocouple Errors"
			error = "There have been {} errors recently. Please check the Thermocouple connection"
			error += "\n and the thermocouple itself for issues."
			error_message(self, error, caption)

		# Fire test tick if we're testing the relay
		if self.testing:
			self.test_tick()

		# Update live visualization if we're running
		if self.toaster.running == STATES.RUNNING:
			self.update_live_visualization()

		# update status grid
		self.update_status_grid()

	def base_notebook_on_notebook_page_changed(self, event):
		"""
		Event handler for notebook page change
		"""
		event.Skip()
		self.init_current_page()

	def temperature_on_radio_button(self, event):
		"""
		Event handler for temperature radio buttons
		"""
		radioBox = event.GetEventObject()
		if radioBox == self.celsius_radio_button and self.units == 'celsius':
			return
		elif radioBox == self.fahrenheit_radio_button and self.units == 'fahrenheit':
			return

		if radioBox == self.celsius_radio_button:
			self.fahrenheit_radio_button.SetValue(False)
			self.units = 'celsius'
		elif radioBox == self.fahrenheit_radio_button:
			self.celsius_radio_button.SetValue(False)
			self.units = 'fahrenheit'

		self.temperature_units_change()
		self.update_temperature_status()

	def save_data_button_on_button_click(self, event):
		"""
		Event handler for save to CSV button
		"""
		event.Skip()
		self.write_data_and_config_to_disk()

	def save_config_menu_item_on_menu_selection(self, event):
		"""
		Event handler for save config menu item
		"""
		event.Skip()
		self.save_config_dialog()

	def load_config_menu_item_on_menu_selection(self, event):
		"""
		Event handler for load config menu item
		"""
		event.Skip()
		self.load_config_dialog()

	def about_menu_item_on_menu_selection(self, event):
		"""
		Event handler for about menu item
		"""
		event.Skip()
		info_message(self, message="See https://www.github.com/imchipwood/Toasting for more info", caption="About")

	def on_close(self, event):
		"""
		Event handler for exit
		"""
		event.Skip()
		self.toaster.cleanup()
		self.Destroy()
		
		# endregion GeneralEventHandlers

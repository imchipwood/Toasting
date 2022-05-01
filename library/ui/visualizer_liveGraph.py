from library.ui.visualizer_configuration import ConfigurationVisualizer, CONFIG_KEY_TARGET
from matplotlib.figure import Figure

# this code was pretty helpful in getting live update working without redrawing entire graph
# https://github.com/eliben/code-for-blog/blob/master/2008/wx_mpl_dynamic_graph.py


class LiveVisualizer(ConfigurationVisualizer):
	def __init__(self, state_configuration, units='celsius'):
		"""
		Live visualizer (line graph) constructor
		@param state_configuration: State config dict for reflow profile
		@type state_configuration: collections.OrderedDict
		@param units: Temperature units to display. Default: celsius
		@type units: str
		"""
		super(LiveVisualizer, self).__init__(state_configuration, draw_lines=True, units=units)
		
		# State tracking
		self.last_state = None
		self.current_state = None

		# seems newer matplotlib versions can have separate axes tics per subplot
		# need to update both
		self.target_state_axes = self.fig.get_axes()

		# Create a new plot
		self.axes = self.fig.add_subplot(111)  # type: Figure
		self.axes.grid(True)
		# self.axes.set_facecolor('black')
		self.axes.set_title("Live Temperature", size=12)

		# Matplotlib plot data structs
		self.state_data_plots = {}  # type: dict[str, matplotlib.lines.Line2D]
		self.state_target_plots = {}  # type: dict[str, matplotlib.lines.Line2D]
		
		# Actual data storage
		self.live_data = []

	def add_data_point(self, x, y, current_target, state_name):
		"""
		Add an X/Y point to the graph
		@param x: x value
		@type x: float
		@param y: y value
		@type y: float
		@param current_target: target Y value
		@type current_target: float
		@param state_name: name of step this datapoint is associated with
		@type state_name: str
		"""
		self.last_state = self.current_state
		self.current_state = state_name
		self.live_data.append([float(x), float(y), float(current_target), state_name])

		self.update_graph()

	def update_graph(self):
		"""
		Update the x/y data of the plots to reflect new data
		"""
		# Create new plot with correct color if new state
		if self.current_state != self.last_state:
			# get the color for this state
			current_target = self.state_configuration[self.current_state][CONFIG_KEY_TARGET]
			
			# Get the target for the last state. If last state doesn't exist, assume target was 0
			if self.last_state:
				last_target = self.state_configuration[self.last_state][CONFIG_KEY_TARGET]
			else:
				last_target = 0

			# Get the color for the current state based on the current & last states
			color = self.getColor(current_target, last_target)

			# make new plot
			self.state_data_plots[self.current_state], = self.axes.plot(
				[],
				linewidth=1,
				color=color,
				marker='x',
				markersize=2
			)
			self.state_target_plots[self.current_state], = self.axes.plot(
				[],
				linewidth=1,
				color='orange',
				marker='o',
				markersize=2
			)

		# gather list of x/y values for this state
		timestamps, temperatures, target_temperatures = self.get_current_state_data()

		# Check if axes limits need to be adjusted
		self.update_axis_limits()

		# For all of our plots, update the X/Y data sets, which forces the plots to re-draw themselves
		self.state_data_plots[self.current_state].set_data(timestamps, temperatures)
		self.state_target_plots[self.current_state].set_data(timestamps, target_temperatures)
		# self.stateDataPlots[self.currentState].set_xdata(timestamps)
		# self.stateDataPlots[self.currentState].set_ydata(temperatures)
		# self.stateTargetPlots[self.currentState].set_xdata(timestamps)
		# self.stateTargetPlots[self.currentState].set_ydata(targetTemperatures)

	def get_current_state_data(self):
		"""
		Get lists of current state data for plotting
		@return: tuple of lists of data - timestamps, current temperatures, target temperatures
		@rtype: tuple[list[float], list[float], list[float]]
		"""
		timestamps = [timestamp for timestamp, currentTemperature, targetTemperature, state in self.live_data if state == self.current_state]
		temperatures = [currentTemperature for x, currentTemperature, targetTemperature, state in self.live_data if state == self.current_state]
		target_temperatures = [targetTemperature for x, y, targetTemperature, state in self.live_data if state == self.current_state]
		return timestamps, temperatures, target_temperatures

	def update_axis_limits(self):
		"""
		Check that axes can display all data and adjust limits if necessary
		"""
		# Get the latest timestamp
		max_timestamp = [timestamp for timestamp, currentTemperature, targetTemperature, state in self.live_data][-1]

		# Is the latest timestamp approaching the end of the X axis?
		x_min, x_max = self.axes.get_xlim()
		if max_timestamp >= (x_max - 50):
			# Yes - increase x-axis limits
			self.axes.set_xlim(right=x_max + 50, emit=True)
			for axis in self.target_state_axes:
				axis.set_xlim(right=x_max + 50, emit=True)

		# Temperatures
		all_temperatures = [currentTemperature for timestamp, currentTemperature, targetTemperature, state in self.live_data]
		all_target_temperatures = [targetTemperature for timestamp, currentTemperature, targetTemperature, state in self.live_data]

		# Is the lowest temperature approaching the y-axis lower limit?
		y_min, y_max = self.axes.get_ylim()
		if min(all_temperatures) <= (y_min + 20) or min(all_target_temperatures) <= (y_min + 20):
			y_min -= 50
		# Is the highest temperature approaching the y-axis upper limit?
		if max(all_temperatures) >= (y_max - 20) or max(all_target_temperatures) >= (y_max - 20):
			y_max += 50

		# Set the new axis limits
		self.axes.set_ylim(y_min, y_max, emit=True)
		for axis in self.target_state_axes:
			axis.set_ylim(y_min, y_max, emit=True)

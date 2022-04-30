from library.ui.visualizer_configuration import ConfigurationVisualizer, CONFIG_KEY_TARGET
from matplotlib.figure import Figure

# this code was pretty helpful in getting live update working without redrawing entire graph
# https://github.com/eliben/code-for-blog/blob/master/2008/wx_mpl_dynamic_graph.py


class LiveVisualizer(ConfigurationVisualizer):
	def __init__(self, stateConfiguration, units='celsius'):
		"""
		Live visualizer (line graph) constructor
		@param stateConfiguration: State config dict for reflow profile
		@type stateConfiguration: collections.OrderedDict
		@param units: Temperature units to display. Default: celsius
		@type units: str
		"""
		super(LiveVisualizer, self).__init__(stateConfiguration, doNotDrawLines=True, units=units)
		
		# State tracking
		self.lastState = None
		self.currentState = None

		# seems newer matplotlib versions can have separate axes tics per subplot
		# need to update both
		self.target_state_axes = self.fig.get_axes()

		# Create a new plot
		self.axes = self.fig.add_subplot(111)  # type: Figure
		self.axes.grid(True)
		# self.axes.set_facecolor('black')
		self.axes.set_title("Live Temperature", size=12)

		# Matplotlib plot data structs
		self.stateDataPlots = {}
		""" @type: dict[str, matplotlib.lines.Line2D] """
		# dict[str, matplotlib.figure.Figure]
		self.stateTargetPlots = {}
		""" @type: dict[str, matplotlib.lines.Line2D] """
		
		# Actual data storage
		self.liveData = []

	def addDataPoint(self, x, y, currentTarget, stateName):
		"""
		Add an X/Y point to the graph
		@param x: x value
		@type x: float
		@param y: y value
		@type y: float
		@param currentTarget: target Y value
		@type currentTarget: float
		@param stateName: name of step this datapoint is associated with
		@type stateName: str
		"""
		self.lastState = self.currentState
		self.currentState = stateName
		self.liveData.append([float(x), float(y), float(currentTarget), stateName])

		self.updateGraph()

	def updateGraph(self):
		"""
		Update the x/y data of the plots to reflect new data
		"""
		# Create new plot with correct color if new state
		if self.currentState != self.lastState:
			# get the color for this state
			currentTarget = self.stateConfiguration[self.currentState][CONFIG_KEY_TARGET]
			
			# Get the target for the last state. If last state doesn't exist, assume target was 0
			if self.lastState:
				lastTarget = self.stateConfiguration[self.lastState][CONFIG_KEY_TARGET]
			else:
				lastTarget = 0

			# Get the color for the current state based on the current & last states
			color = self.getColor(currentTarget, lastTarget)

			# make new plot
			self.stateDataPlots[self.currentState], = self.axes.plot(
				[],
				linewidth=1,
				color=color,
				marker='x',
				markersize=2
			)
			self.stateTargetPlots[self.currentState], = self.axes.plot(
				[],
				linewidth=1,
				color='orange',
				marker='o',
				markersize=2
			)

		# gather list of x/y values for this state
		timestamps, temperatures, targetTemperatures = self.getCurrentStateData()

		# Check if axes limits need to be adjusted
		self.updateAxesLimits()

		# For all of our plots, update the X/Y data sets, which forces the plots to re-draw themselves
		self.stateDataPlots[self.currentState].set_data(timestamps, temperatures)
		self.stateTargetPlots[self.currentState].set_data(timestamps, targetTemperatures)
		# self.stateDataPlots[self.currentState].set_xdata(timestamps)
		# self.stateDataPlots[self.currentState].set_ydata(temperatures)
		# self.stateTargetPlots[self.currentState].set_xdata(timestamps)
		# self.stateTargetPlots[self.currentState].set_ydata(targetTemperatures)

	def getCurrentStateData(self):
		"""
		Get lists of current state data for plotting
		@return: tuple of lists of data - timestamps, current temperatures, target temperatures
		@rtype: tuple[list[float], list[float], list[float]]
		"""
		timestamps = [timestamp for timestamp, currentTemperature, targetTemperature, state in self.liveData if state == self.currentState]
		temperatures = [currentTemperature for x, currentTemperature, targetTemperature, state in self.liveData if state == self.currentState]
		targetTemperatures = [targetTemperature for x, y, targetTemperature, state in self.liveData if state == self.currentState]
		return timestamps, temperatures, targetTemperatures

	def updateAxesLimits(self):
		"""
		Check that axes can display all data and adjust limits if necessary
		"""
		# Get the latest timestamp
		maxTimestamp = [timestamp for timestamp, currentTemperature, targetTemperature, state in self.liveData][-1]

		# Is the latest timestamp approaching the end of the X axis?
		xMin, xMax = self.axes.get_xlim()
		if maxTimestamp >= (xMax - 50):
			# Yes - increase x-axis limits
			self.axes.set_xlim(right=xMax + 50, emit=True)
			for axis in self.target_state_axes:
				axis.set_xlim(right=xMax + 50, emit=True)

		# Temperatures
		allTemperatures = [currentTemperature for timestamp, currentTemperature, targetTemperature, state in self.liveData]
		allTargetTemperatures = [targetTemperature for timestamp, currentTemperature, targetTemperature, state in self.liveData]

		# Is the lowest temperature approaching the y-axis lower limit?
		yMin, yMax = self.axes.get_ylim()
		if min(allTemperatures) <= (yMin + 20) or min(allTargetTemperatures) <= (yMin + 20):
			yMin -= 50
		# Is the highest temperature approaching the y-axis upper limit?
		if max(allTemperatures) >= (yMax - 20) or max(allTargetTemperatures) >= (yMax - 20):
			yMax += 50

		# Set the new axis limits
		self.axes.set_ylim(yMin, yMax, emit=True)
		for axis in self.target_state_axes:
			axis.set_ylim(yMin, yMax, emit=True)

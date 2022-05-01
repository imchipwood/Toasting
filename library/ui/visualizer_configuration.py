import matplotlib
matplotlib.use("WXAgg")
import matplotlib.lines as mlines
from matplotlib.figure import Figure

from definitions import CONFIG_KEY_TARGET, CONFIG_KEY_DURATION

COLORS = {
	'+': 'red',
	'==': 'green',
	'-': 'blue',
	None: 'yellow'
}


class ConfigurationVisualizer:
	def __init__(self, state_configuration, draw_lines=True, units='celsius'):
		"""
		Configuration visualizer (line graph) constructor
		@param state_configuration: State config dict for reflow profile
		@type state_configuration: collections.OrderedDict
		@param draw_lines: flag to disable drawing the lines of the configuration. Default: False
		@type draw_lines: bool
		@param units: Temperature units to display. Default: celsius
		@type units: str
		"""
		super().__init__()
		self.state_configuration = state_configuration

		if self.state_configuration:
			# Get the maximum temps & timestamps from the config and increase them by 50 to use as axes limits
			max_target_temp = self.getMaxValueFromStateConfig(CONFIG_KEY_TARGET, method=max) + 50
			max_timestamp = self.getMaxValueFromStateConfig(CONFIG_KEY_TARGET, method=sum) + 50
		else:
			max_target_temp = 300
			max_timestamp = 300

		# Create a plot and save it for use later
		self.fig = self.createPlot(
			self.state_configuration,
			doNotDrawLines=draw_lines,
			units=units,
			maxTargetTemp=max_target_temp,
			maxTimestamp=max_timestamp
		)

	def getMaxValueFromStateConfig(self, configKey, method=max):
		"""
		Get the max value for the particular key in the state configuration
		@param configKey: key to use to get values from dict
		@type configKey: str
		@param method: the method to use for finding the max. Default: max. Other valid operations: sum, min,
		@type method: function
		@return: Max value based on given configKey & method
		@rtype: float
		"""
		return method([float(stateConfig[configKey]) for stateConfig in self.state_configuration.values()])

	def createPlot(self, stateConfiguration=None, doNotDrawLines=False, units='celsius', maxTargetTemp=300, maxTimestamp=500) -> Figure:
		"""
		Create a plot and return it
		@param stateConfiguration: state configuration dictionary. Default: None
		@type stateConfiguration: collections.OrderedDict
		@param doNotDrawLines: flag to disable drawing the lines of the configuration. Default: False
		@type doNotDrawLines: bool
		@param units: temperature units to display (used in Y axis label)
		@type units: str
		@param maxTargetTemp: maximum target temp to use in plot (for scaling Y axis)
		@type maxTargetTemp: int or float
		@param maxTimestamp: maximum timestamp to use in plot (for scaling X axis)
		@type maxTimestamp: int or float
		@return: The new plot figure
		@rtype: matplotlib.figure.Figure
		"""
		# State config may not have been passed in - if not, use the one passed to the constructor
		stateConfiguration = stateConfiguration or self.state_configuration

		# Base figure & axes
		fig = Figure()
		axis = fig.add_subplot(111)
		axis.grid(True)

		if doNotDrawLines:
			# Simply set the axis limits on the graph
			axis.set_ylim(0, maxTargetTemp)
			axis.set_xlim(0, maxTimestamp)
		else:
			cumulativeTimestamp = 0
			previousStateTargetTemperature = 0

			# Create a line graph for each stage in the desired reflow profile
			for step, currentStateConfig in stateConfiguration.items():
				currentStateTargetTemperature = currentStateConfig[CONFIG_KEY_TARGET]
				currentStateDuration = currentStateConfig[CONFIG_KEY_DURATION]

				# X-axis start/end values
				currentStateStartTimestamp = cumulativeTimestamp
				currentStateEndTimestamp = cumulativeTimestamp + currentStateDuration

				# Y-axis start/end values
				currentStateStartTemperature = previousStateTargetTemperature
				currentStateEndTemperature = currentStateTargetTemperature

				# Draw the line and add it to the graph
				line = mlines.Line2D(
					[currentStateStartTimestamp, currentStateEndTimestamp],
					[currentStateStartTemperature, currentStateEndTemperature],
					color=self.getColor(currentStateTargetTemperature, previousStateTargetTemperature),
					linewidth=1
				)
				axis.add_line(line)

				# Track
				cumulativeTimestamp = currentStateEndTimestamp
				previousStateTargetTemperature = currentStateTargetTemperature

			axis.autoscale(True)

		# Set the timestamps
		axis.set_xlabel('Timestamp (seconds)')
		yLabel = 'Temperature ({})'.format(units.capitalize())
		axis.set_ylabel(yLabel)

		# Move bottom graph edge up a bit to ensure x-axis label is visible
		fig.subplots_adjust(bottom=0.15)

		return fig

	@staticmethod
	def getColor(currentTarget, lastTarget):
		"""
		Get the correct color for a stage based on temperature delta
		@param currentTarget: target temp for current state
		@type currentTarget: float
		@param lastTarget: target temp for last state
		@type lastTarget: float
		@return: Color code
		@rtype: str
		"""
		if currentTarget > lastTarget:
			color = COLORS['+']
		elif currentTarget == lastTarget:
			color = COLORS['==']
		elif currentTarget < lastTarget:
			color = COLORS['-']
		else:
			color = COLORS[None]
		return color

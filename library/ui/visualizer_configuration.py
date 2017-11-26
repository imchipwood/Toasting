import matplotlib
matplotlib.use("WXAgg")
import matplotlib.lines as mlines
from matplotlib.figure import Figure

CONFIG_KEY_TARGET = "target"
CONFIG_KEY_DURATION = "duration"

COLORS = {
	'+': 'red',
	'==': 'green',
	'-': 'blue'
}


class ConfigurationVisualizer(object):
	def __init__(self, stateConfiguration, doNotDraw=False, units='celcius'):
		super(ConfigurationVisualizer, self).__init__()
		self.stateConfiguration = stateConfiguration

		# Get the maximum temps & timestamps from the config and increase them by 50 to use as axes limits
		maxTargetTemp = max([stateConfig[CONFIG_KEY_TARGET] for stateName, stateConfig in self.stateConfiguration.items()])
		maxTargetTemp += 50
		maxTimestamp = sum([stateConfig[CONFIG_KEY_DURATION] for stateName, stateConfig in self.stateConfiguration.items()])
		maxTimestamp += 50

		# Create a plot and save it for use later
		self.fig = self.createPlot(
			self.stateConfiguration,
			doNotDraw=doNotDraw,
			units=units,
			maxTargetTemp=maxTargetTemp,
			maxTimestamp=maxTimestamp
		)

	def createPlot(self, stateConfiguration=None, doNotDraw=False, units='celcius', maxTargetTemp=300, maxTimestamp=500):
		"""Create a plot and return it

		@param configurationDict: Configuration info
		@type configurationDict: OrderedDict

		@return: matplotlib.figure.Figure
		"""
		if not stateConfiguration:
			stateConfiguration = self.stateConfiguration

		fig = Figure()
		axis = fig.add_subplot(111)

		if not doNotDraw:
			currentTimestamp = 0
			lastTarget = 0

			for step, stateInfo in stateConfiguration.items():
				target = stateInfo[CONFIG_KEY_TARGET]
				duration = stateInfo[CONFIG_KEY_DURATION]

				xmin = currentTimestamp
				xmax = currentTimestamp + duration

				ymin = lastTarget
				ymax = target

				line = mlines.Line2D(
					[xmin, xmax],
					[ymin, ymax],
					color=self.getColor(target, lastTarget),
					linewidth=1
				)
				axis.add_line(line)

				currentTimestamp += duration
				lastTarget = target

			axis.autoscale(True)
		else:
			axis.set_xlim(0, maxTimestamp)
			axis.set_ylim(0, maxTargetTemp)

		axis.set_xlabel('Timestamp (seconds)')
		yLabel = 'Temperature ({})'.format(units[0].upper())
		axis.set_ylabel(yLabel)
		axis.grid(True)

		# adjust bottom so xlabel shows up... because matplotlib is stupid
		fig.subplots_adjust(bottom=0.15)

		return fig

	@staticmethod
	def getColor(currentTarget, lastTarget):
		"""Get the correct color for a stage based on temperature delta

		@param currentTarget: target temp
		@type currentTarget: float
		@param lastTarget: last target temp
		@type lastTarget: float
		@return: str
		"""
		if currentTarget > lastTarget:
			color = COLORS['+']
		elif currentTarget == lastTarget:
			color = COLORS['==']
		elif currentTarget < lastTarget:
			color = COLORS['-']
		return color

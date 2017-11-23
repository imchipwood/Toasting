from library.ui.visualizer_configuration import ConfigurationVisualizer, CONFIG_KEY_TARGET

# this code was pretty helpful in getting live update working without redrawing entire graph
# https://github.com/eliben/code-for-blog/blob/master/2008/wx_mpl_dynamic_graph.py


class LiveVisualizer(ConfigurationVisualizer):
	def __init__(self, stateConfiguration, redrawCallback=None, units='celcius'):
		super(LiveVisualizer, self).__init__(stateConfiguration, doNotDraw=True, units=units)
		self.lastStepNum = 0
		self.originalFig = self.fig

		self.redrawCallback = redrawCallback

		self.lastState = None
		self.currentState = None
		self.liveData = []
		self.lines = {}

		self.axes = self.fig.add_subplot(111)
		self.axes.grid(True)
		# self.axes.set_facecolor('black')
		self.axes.set_title("Live Temperature", size=12)
		self.stateDataPlots = {}
		self.stateTargetPlots = {}

	def addDataPoint(self, x, y, currentTarget, stateName):
		"""Add an X/Y point to the graph

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
		"""Redraw the graph, adding any new points to the plot"""
		# Create new plot with correct color if new state
		if self.currentState != self.lastState:
			# get the color for this state
			currentTarget = self.stateConfiguration[self.currentState][CONFIG_KEY_TARGET]
			if self.lastState:
				lastTarget = self.stateConfiguration[self.lastState][CONFIG_KEY_TARGET]
			else:
				lastTarget = 0
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
		xList = [x for x, y, target, state in self.liveData if state == self.currentState]
		yList = [y for x, y, target, state in self.liveData if state == self.currentState]
		targetYList = [target for x, y, target, state in self.liveData if state == self.currentState]

		# update plot data for this state
		self.stateDataPlots[self.currentState].set_xdata(xList)
		self.stateDataPlots[self.currentState].set_ydata(yList)
		self.stateTargetPlots[self.currentState].set_xdata(xList)
		self.stateTargetPlots[self.currentState].set_ydata(targetYList)

		# redraw if we got a callback
		if self.redrawCallback:
			self.redrawCallback()

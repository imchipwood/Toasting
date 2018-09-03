import json
import os
from collections import OrderedDict

import matplotlib

matplotlib.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

import wx

from library.ui.ToastingGUIBase import GraphTestFrame
from library.ui.visualizer_configuration import ConfigurationVisualizer, CONFIG_KEY_TARGET, CONFIG_KEY_DURATION
from library.ui.visualizer_liveGraph import LiveVisualizer


class ConfigurationGraphTestPanel(GraphTestFrame):
	def __init__(self, parent, stateConfiguration=None):
		super(ConfigurationGraphTestPanel, self).__init__(parent)

		# GUI vars
		self.canvas = None
		self.stateConfiguration = None
		self.visualizer = None

		self.Bind(wx.EVT_CLOSE, self.onClose)

		# Config vars
		if stateConfiguration:
			self.updateConfiguration(stateConfiguration)

	def updateConfiguration(self, newStateConfiguration):
		"""
		Redraw state visualization
		@param newStateConfiguration: new config to draw
		@type newStateConfiguration: dict
		"""
		self.stateConfiguration = newStateConfiguration
		self.visualizer = ConfigurationVisualizer(self.stateConfiguration)
		self.addFigToPanel(fig=self.visualizer.fig)

	def addFigToPanel(self, fig):
		"""Update the figure in the panel

		@param fig: Figure to put on the panel
		@type fig: matplotlib.figure.Figure
		"""
		# Clear items out of sizer
		sizer = self.graphTestBasePanel.GetSizer()
		sizer.Clear()
		sizer.Layout()

		# Create a canvas for the plot frame
		self.canvas = FigureCanvas(self.graphTestBasePanel, -1, fig)

		# get the sizer for the plot panel and add canvas to it
		sizer.Add(self.canvas, 1, wx.EXPAND)
		self.Layout()

	def onClose(self, event):
		"""Event handler for exit

		@param event: wx.EVT_CLOSE
		"""
		event.Skip()
		self.Destroy()


class LiveGraphTestPanel(ConfigurationGraphTestPanel):
	def __init__(self, parent, stateConfiguration):
		super(LiveGraphTestPanel, self).__init__(parent, stateConfiguration)

		# Set up a timer
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.timerHandler)

		# Create the configurationVisualizer
		self.visualizer = LiveVisualizer(self.stateConfiguration)
		self.fig = self.visualizer.fig
		self.addFigToPanel(self.fig)
		
		# State machine
		self.statePeriod = 0.5
		self.states = list(self.stateConfiguration.keys())
		self.stateIndex = 0
		self.currentState = self.states[self.stateIndex]
		self.currentStateEnd = self.stateConfiguration[self.currentState][CONFIG_KEY_DURATION]
		self.currentTarget = self.stateConfiguration[self.currentState][CONFIG_KEY_TARGET]

		# Counters
		self.timestamp = 0.0
		self.y = 10.0

		# How much to add every tick
		self.yAdder = self.currentTarget * (self.statePeriod / self.currentStateEnd)

		# Initialize graph
		self.updateGraph()

		# Start timer
		self.timer.Start(self.statePeriod * 1000)

	def timerHandler(self, event):
		"""Update live graph

		@param event: wx.EVT_TIMER
		"""
		event.Skip()

		# update state machine counters
		self.timestamp += 0.5
		self.y += self.yAdder

		# Check if ready to move to next state
		if self.timestamp == self.currentStateEnd:
			self.nextState()

		# Update graph
		self.updateGraph()

	def nextState(self):
		"""Update necessary counters/etc. for next stage"""
		# Update state
		self.stateIndex += 1
		self.currentState = self.states[self.stateIndex]

		# Calculate the adder for this new state
		duration = self.stateConfiguration[self.currentState][CONFIG_KEY_DURATION]
		target = self.stateConfiguration[self.currentState][CONFIG_KEY_TARGET]
		self.yAdder = (target - self.currentTarget) * (self.statePeriod / duration)

		# Update the rest of the state variables
		self.currentTarget = target
		self.currentStateEnd += duration

	def updateGraph(self):
		"""Update the graph with latest date point"""
		self.visualizer.addDataPoint(self.timestamp, self.y, self.currentTarget, self.currentState)
		self.canvas.draw()


if __name__ == "__main__":
	app = wx.App()

	# Open a fake config
	from definitions import GetBaseConfigurationFilePath
	with open(GetBaseConfigurationFilePath()) as inf:
		config = json.load(inf, object_pairs_hook=OrderedDict)
		config = config['states']

	# create the config graph test panel and update the config
	# view = ConfigurationGraphTestPanel(
	# 	parent=None,
	# 	stateConfiguration=config
	# )
	# updatedConfig = deepcopy(config)
	# updatedConfig['preheat']['duration'] = 60.0
	# view.updateConfiguration(updatedConfig)
	# view.Show()

	# create the live graph panel and show it
	view2 = LiveGraphTestPanel(
		parent=None,
		stateConfiguration=config
	)
	view2.Show()
	app.SetTopWindow(view2)

	app.MainLoop()

from collections import defaultdict, Counter
from functools import wraps
from threading import Lock
from wx.lib.pubsub import pub

BusyCounterDict = Counter()
LocksDict = defaultdict(lambda: Lock())


def sendBusySignal(modelName):
	with LocksDict[modelName]:
		# increment counter for busy indicating that it's busy
		BusyCounterDict[modelName] = BusyCounterDict[modelName] + 1
		# send ready signal if all other ready signals finished
		if BusyCounterDict[modelName] >= 1:
			pub.sendMessage('{}_BUSY'.format(modelName))


def sendReadySignal(modelName):
	with LocksDict[modelName]:
		# decrement counter
		BusyCounterDict[modelName] = BusyCounterDict[modelName] - 1
		# send ready signal if all other ready signals finished
		if BusyCounterDict[modelName] == 0:
			pub.sendMessage('{}_READY'.format(modelName))


def BusyReady(modelName):
	def actualDecorator(function):
		@wraps(function)
		def wrapper(*args, **kwargs):
			try:
				# Call the busy function
				sendBusySignal(modelName)
				print("BUSY: {}".format(function.__name__))
				# Call the actual function
				return function(*args, **kwargs)
			finally:
				# Call the ready function
				sendReadySignal(modelName)
				print("READY: {}".format(function.__name__))
				print("COUNTERS: {}".format(BusyCounterDict[modelName]))

		return wrapper

	return actualDecorator


def subscribeToBusySignal(function, modelName):
	# subscribe the given function to the busy signal for the the given model
	pub.subscribe(function, '{}_BUSY'.format(modelName))


def subscribeToReadySignal(function, modelName):
	# subscribe the given function to the ready signal for the the given model
	pub.subscribe(function, '{}_READY'.format(modelName))

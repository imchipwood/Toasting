import os
import time
import logging
import json
from collections import OrderedDict
from threading import Thread

from library.control.stateMachine import STATES, ToastStateMachine
from definitions import GetConfigurationFilePath, GetBaseConfigurationFilePath, GetDataFilePath

global TOASTER
TOASTER = None

KEY_STATE_MACHINE_TICK = "StateMachineTick"


def setup_module(module):
	return


def teardown_module(module):
	global TOASTER
	if TOASTER:
		TOASTER.cleanup()


def setup_function(function):
	return


def teardown_function(function):
	return


def GetStateMachine(new=True, debugLevel=logging.INFO, configFile=GetBaseConfigurationFilePath()):
	global TOASTER
	if new:
		if TOASTER:
			TOASTER.cleanup()
		TOASTER = ToastStateMachine(configFile, debugLevel=debugLevel)
	return TOASTER


class ClockThread(Thread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
		super(ClockThread, self).__init__(group=group, target=target, name=name, args=args, kwargs=kwargs)
		self.running = False
		self.tick = kwargs.get(KEY_STATE_MACHINE_TICK, self._dummyTick) if kwargs else self._dummyTick

	def _dummyTick(self):
		return

	def start(self):
		self.running = True
		super(ClockThread, self).start()

	def run(self):
		super(ClockThread, self).run()
		while self.running:
			self.tick()

	def stop(self):
		self.running = False


def tickNTimes(sm, n):
	for i in range(n):
		sm.tick()


def test_Tick():
	"""
	Test that the tick method stores data
	Also test the __repr__ method
	"""
	sm = GetStateMachine()

	try:
		sm.start()
		assert sm.running == STATES.RUNNING

		tickNTimes(sm, 5)
		assert sm.relayState

		assert sm.running == STATES.RUNNING
		print("Calling next state")
		sm.nextState()
		print("Ticking more")
		assert sm.currentState == sm.states[1]
		tickNTimes(sm, 121)
		assert str(sm) == "{}:{}".format(STATES.RUNNING, sm.states[2])
		assert sm.currentState == sm.states[2]

		assert sm.data
		assert sm.getRecentErrorCount() == 0

	finally:
		sm.cleanup()


def test_TickTest():
	"""
	Test that the 'testing' arg of ticking works
	"""
	sm = GetStateMachine()
	try:
		sm.start()
		tickNTimes(sm, 10)
		assert sm.relayState
		sm.stop()
		sm.tick(testing=True)
		assert sm.relayState
	finally:
		sm.cleanup()


def test_NextState():
	"""
	Test that calling next state increments the state
	"""
	sm = GetStateMachine()

	try:
		sm.start()
		assert sm.running == STATES.RUNNING

		for i in range(len(sm.states)):
			assert sm.currentState == sm.states[i]
			sm.nextState()

		assert sm.running == STATES.COMPLETE

	finally:
		sm.cleanup()


def test_RunFree_PauseResume():
	"""
	Test that the state machine can run its full course
	Also test pausing & resuming
	"""
	sm = GetStateMachine()
	try:
		# start the state machine
		sm.start()
		assert sm.running == STATES.RUNNING

		# start the clock tick thread
		thread = ClockThread(kwargs={KEY_STATE_MACHINE_TICK: sm.tick})
		thread.start()

		i = 0
		pauseTimestamp = 250
		resumeTimestamp = 350
		lastTimestamp = 0
		while sm.running != STATES.COMPLETE:

			# Increment the state occasionally
			if i % 200 == 0 and i != 0:
				sm.nextState()

			# Pause/resume
			if i == pauseTimestamp:
				sm.pause()
				assert sm.running == STATES.PAUSED
			if i == resumeTimestamp:
				sm.resume()
				assert sm.running == STATES.RUNNING

			if pauseTimestamp < i <= resumeTimestamp:
				assert sm.timestamp == lastTimestamp, "timestamp changed @ {}".format(i)
			else:
				lastTimestamp = sm.timestamp

			i += 1
			if i > 10000:
				assert False, "state machine never ended"

		thread.stop()
		sm.stop()
		assert sm.running == STATES.STOPPED
		assert sm.currentState == sm.states[0]

	finally:
		sm.cleanup()


def test_DumpDataToCsv():
	"""
	Test that dumping data after state machine fully completes works
	"""
	sm = GetStateMachine(new=True)
	sm.stateConfiguration['cooling']['target'] = -5

	assert not sm.dumpDataToCsv("somePath")
	try:
		# start the state machine
		sm.start()
		assert sm.running == STATES.RUNNING

		# start the clock tick thread
		thread = ClockThread(kwargs={KEY_STATE_MACHINE_TICK: sm.tick})
		thread.start()

		i = 0
		while sm.running != STATES.COMPLETE:
			time.sleep(0.001)

			# Increment the state occasionally
			if i % 20 == 0 and i != 0:
				sm.nextState()

			i += 1
			if i > 10000:
				assert False, "state machine never ended"

		thread.stop()

		# Remove dump file if it exists
		dumpPath = GetDataFilePath("testData.csv")
		if os.path.exists(dumpPath):
			try:
				os.remove(dumpPath)
			except:
				print("Failed to remove test data file - moving on")
				raise

		# Dump to CSV
		assert sm.dumpDataToCsv(dumpPath)
		assert os.path.exists(dumpPath)

		# Check that the first and last lines in the dump file match the expected states
		with open(dumpPath, 'r') as inf:
			lines = inf.readlines()
			assert sm.states[0] in lines[1]
			assert sm.states[-1] in lines[-1]

		# Remove the test dump file
		try:
			os.remove(dumpPath)
		except:
			print("Failed to remove test data file at end of test- moving on")

	finally:
		sm.cleanup()


def test_setAlternateConfig():
	"""
	Test setting an alternate config file after already creating the state machine works
	"""
	sm = GetStateMachine()
	try:
		sm.config = GetConfigurationFilePath("dummyConfig.json")
		assert sm.relay.pin == 101
		assert sm.timerPeriod == 1
		assert sm.pid.kP == 10.6

		testDump = GetConfigurationFilePath("testConfigDump.json")
		if os.path.exists(testDump):
			os.remove(testDump)

		sm.dumpConfig(testDump)

		with open(testDump, 'r') as inf:
			testConfig = json.load(inf, object_pairs_hook=OrderedDict)

		assert sm.config.config == testConfig
		os.remove(testDump)
	finally:
		sm.cleanup()


def test_settersGetters():
	"""
	Test some of the config setters & getters
	"""
	sm = GetStateMachine(configFile=None)
	try:
		sm.units = 'fahrenheit'
		assert sm.units == 'fahrenheit'
		sm.units = 'celsius'
		assert sm.units == 'celsius'

		assert sm.pid

		sm.timerPeriod = 10
		assert sm.timerPeriod == 10
	finally:
		sm.cleanup()


def test_setStateConfiguration():
	"""
	Test setting the state configuration works
	"""
	sm = GetStateMachine(configFile=None)
	try:
		assert sm.states == []

		with open(GetConfigurationFilePath("dummyConfig.json"), 'r') as inf:
			tmpConfig = json.load(inf, object_pairs_hook=OrderedDict)

		sm.stateConfiguration = tmpConfig['states']

		assert sm.states
		assert sm.states[0] == 'ramp2soak'
		assert sm.stateConfiguration['ramp2soak']['target'] == 125
	finally:
		sm.cleanup()

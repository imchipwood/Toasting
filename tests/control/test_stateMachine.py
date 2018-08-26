import os
import time
import logging
from threading import Thread

from library.control.stateMachine import STATES, ToastStateMachine
from definitions import GetBaseConfigurationFilePath, GetDataFilePath

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


def GetStateMachine(new=True, debugLevel=logging.INFO):
	global TOASTER
	if new:
		if TOASTER:
			TOASTER.cleanup()
		TOASTER = ToastStateMachine(GetBaseConfigurationFilePath(), debugLevel=debugLevel)
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
	Test that the state machine can go its course
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

	finally:
		sm.cleanup()


def test_DumpDataToCsv():
	"""
	Test that dumping data to CSV works
	"""
	sm = GetStateMachine(new=True)
	sm.stateConfiguration['cooling']['target'] = -5
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
		sm.dumpDataToCsv(dumpPath)
		assert os.path.exists(dumpPath)

		# Check that the first and last lines in the dump file match the states
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

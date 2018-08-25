import random
import pytest

from library.control.pid import PID


def setup_module(module):
	return


def teardown_module(module):
	return


def setup_function(function):
	return


def teardown_function(function):
	return


def getPID():
	settings = {
		"kP": 1.0,
		"kI": 0.01,
		"kD": 10.0,
		"min": "",
		"max": "",
		"windupGuard": 20.0,
	}
	return PID(settings)


def test_compute():
	"""
	Test that the PID computation doesn't error out
	"""
	pid = getPID()
	pid.target = 100.0

	timeInterval = 0.5
	currentTime = 0.0
	currentState = 10.0
	out = pid.compute(currentTime, currentState)
	for i in range(1000):
		# Increment time
		currentTime += timeInterval
		out = pid.compute(currentTime, currentState)

		# Confirm windup guard is working
		assert -pid.windupGuard <= pid.ierror <= pid.windupGuard

		# Increment state
		multiplier = 1 if i % 2 == 0 else -1
		adder = (random.randint(0, 1000) / 100.0) * multiplier
		currentState += adder


def test_zeroierror():
	"""
	Test that IError changes when we compute, and test that zeroing works
	"""
	pid = getPID()
	pid.target = 100.0
	pid.compute(0, 10.0)
	pid.compute(1, 10.0)
	assert pid.ierror != 0
	pid.zeroierror()
	assert pid.ierror == 0


def test_min_max():
	"""
	Test that setting min and max values appropriately works
	Also test that setting them incorrectly raises exceptions
	"""
	pid = getPID()
	pid.target = 100.0
	pid.compute(0, 10.0)
	pid.compute(1, 10.0)

	pid.min = 0
	with pytest.raises(Exception, message="expected assertion error for max < min value"):
		pid.max = -10

	pid.max = 10

	with pytest.raises(Exception, message="expected assertion error for min > max value"):
		pid.min = 11

	timeInterval = 0.5
	currentTime = 0.0
	currentState = 10.0
	out = pid.compute(currentTime, currentState)
	for i in range(1000):
		# Increment time
		currentTime += timeInterval
		out = pid.compute(currentTime, currentState)

		assert pid.min <= out <= pid.max

		# Increment state
		multiplier = 1 if i % 2 == 0 else -1
		adder = (random.randint(0, 1000) / 100.0) * multiplier
		currentState += adder

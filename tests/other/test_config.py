import os
import json
import pytest
from collections import OrderedDict

from library.other.config import ToasterConfig
from library.control.pid import PID
from definitions import GetBaseConfigurationFilePath


def setup_module(module):
	return


def teardown_module(module):
	return


def setup_function(function):
	return


def teardown_function(function):
	return


def test_ToasterConfig():
	"""
	Test that loading a config at least stores the proper types
	"""
	config = ToasterConfig(GetBaseConfigurationFilePath())
	assert isinstance(config.pids, PID)
	assert isinstance(config.pids.kP, (float, int))
	assert isinstance(config.pins, dict)
	assert isinstance(config.spiCsPin, int)
	assert isinstance(config.relayPin, int)
	assert isinstance(config.clockPeriod, (float, int))


def test_NonDefaults(monkeypatch):
	"""
	Test that the configuration was actually loaded by monkeypatching a bunch of
	crap into the ToasterConfig class. Check that the config was loaded by ensuring the
	fake data is not returned when we access config attributes
	"""
	fakeUnits = "some fake value"
	fakePins = {
		"SPI_CS": 12341,
		"relay": 234234
	}
	fakePeriod = -10
	fakePID = "not a PID object"
	monkeypatch.setattr(ToasterConfig, 'BASE_UNITS', fakeUnits)
	monkeypatch.setattr(ToasterConfig, 'BASE_PINS', fakePins)
	monkeypatch.setattr(ToasterConfig, 'BASE_CLOCK_PERIOD', fakePeriod)
	monkeypatch.setattr(ToasterConfig, 'BASE_PID', fakePID)

	config = ToasterConfig(GetBaseConfigurationFilePath())
	assert config.units != fakeUnits
	assert config.pins != fakePins
	assert config.clockPeriod != fakePeriod
	assert config.pids != fakePID
	assert isinstance(config.pids, PID)


def test_setters():
	"""
	Test all of the setters & getters
	"""
	config = ToasterConfig(GetBaseConfigurationFilePath())

	config.relayPin = 50
	assert config.relayPin == 50

	config.spiCsPin = 1
	assert config.spiCsPin == 1
	config.spiCsPin = 0
	assert config.spiCsPin == 0

	config.units = 'fahrenheit'
	assert config.units == 'fahrenheit'
	config.units = 'celsius'
	assert config.units == 'celsius'
	with pytest.raises(Exception):
		# "Expected exception for invalid units"
		config.units = "FAKEUNITS"

	config.pids = PID()
	config.pids = {'kP': 1234}
	assert config.pids.kP == 1234

	config.clockPeriod = 0.25
	assert config.clockPeriod == 0.25

	testStates = OrderedDict()
	testStates['firstState'] = {
		"target": 999,
		"duration": 999
	}
	config.states = testStates
	assert config.states['firstState']['target'] == 999

	with pytest.raises(Exception):
		# "Expected exception for invalid states type"
		config.states = ['bob', 'was', 'here']

	# Test setting the config
	assert config.units != 'fahrenheit'
	config.config = {'units': 'fahrenheit'}
	assert config.units == 'fahrenheit'


def test_dumpConfig():
	"""
	Test dumping the config to a file works
	"""
	config = ToasterConfig(GetBaseConfigurationFilePath())

	# make a test dump and clean up the old one if it's lying around
	testDump = GetBaseConfigurationFilePath().replace(".json", "_test.json")
	if os.path.exists(testDump):
		os.remove(testDump)

	# Dump our config and make sure it exists
	config.dumpConfig(testDump)
	assert os.path.exists(testDump)

	# load the config we just dumped
	with open(testDump, 'r') as inf:
		testConfig = json.load(inf, object_pairs_hook=OrderedDict)

	# remove the config
	os.remove(testDump)

	assert testConfig == config.config

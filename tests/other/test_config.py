import os

from library.other.config import ToasterConfig
from library.control.pid import PID

global CONFIG_PATH


def setup_module(module):
	global CONFIG_PATH
	CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "baseConfig.json")


def teardown_module(module):
	return


def setup_function(function):
	return


def teardown_function(function):
	return


def test_ToasterConfig():
	config = ToasterConfig(CONFIG_PATH)
	assert isinstance(config.pids, PID)
	assert isinstance(config.pids.kP, (float, int))
	assert isinstance(config.spiCsPin, int)
	assert isinstance(config.relayPin, int)
	assert isinstance(config.clockPeriod, (float, int))
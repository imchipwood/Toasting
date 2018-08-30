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
	config = ToasterConfig(GetBaseConfigurationFilePath())
	assert isinstance(config.pids, PID)
	assert isinstance(config.pids.kP, (float, int))
	assert isinstance(config.spiCsPin, int)
	assert isinstance(config.relayPin, int)
	assert isinstance(config.clockPeriod, (float, int))
	
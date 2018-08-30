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


def test_NonDefaults(monkeypatch):
	"""
	Test that the configuration was actually loaded by monkeypatching a bunch of
	crap into the ToasterConfig class
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

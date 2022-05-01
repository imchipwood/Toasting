from library.other.config import ToasterConfig
from library.sensors.sensor_relay import Relay
from definitions import get_base_configuration_file_path

global RELAY_PIN


def setup_module(module):
	global RELAY_PIN
	config = ToasterConfig(get_base_configuration_file_path())
	RELAY_PIN = config.relayPin


def teardown_module(module):
	return


def setup_function(function):
	return


def teardown_function(function):
	return


def test_initDisable():
	"""
	Test that creating a relay with startingState False does just that
	"""
	try:
		relay = Relay(pin=RELAY_PIN, startingState=False)
		assert relay.pin == RELAY_PIN
		assert relay.state is False

		relay.enable()
		assert relay.state is True

		relay.disable()
		assert relay.state is False
	finally:
		relay.cleanup()


def test_initEnable():
	"""
	Test that creating a relay with startingState True does just that
	"""
	try:
		relay = Relay(pin=RELAY_PIN, startingState=True)
		assert relay.pin == RELAY_PIN
		assert relay.state is True

		relay.disable()
		assert relay.state is False

		relay.enable()
		assert relay.state is True
	finally:
		relay.cleanup()


def test_toggle():
	"""
	Test that creating a relay with startingState True does just that
	"""
	try:
		relay = Relay(pin=RELAY_PIN, startingState=True)
		assert relay.pin == RELAY_PIN
		assert relay.state is True

		relay.toggle()
		assert relay.state is False

		relay.toggle()
		assert relay.state is True
	finally:
		relay.cleanup()

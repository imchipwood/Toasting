import os

from library.control.stateMachine import ToastStateMachine
from library.sensors.sensor_relay import Relay

global RELAY_PIN


def setup_module(module):
	global RELAY_PIN
	configPath = os.path.join(os.path.dirname(__file__), "..", "..", "config", "baseConfig.json")
	RELAY_PIN = ToastStateMachine.getConfigFromJsonFile(configPath).get("pins", {}).get("relay", -1)


def teardown_module(module):
	return


def setup_function(function):
	return


def teardown_function(function):
	return


def test_Relay_initDisable():
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


def test_Relay_initEnable():
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

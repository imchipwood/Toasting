import sys
import os
sys.path.append(os.path.join("/".join(os.path.realpath(__file__).split('/')[:-2]), 'library'))
from sensor_relay import Relay
import RPi.GPIO as GPIO
from time import sleep
import timeit
import logging


def test_relay():
	logging.getLogger().setLevel(logging.DEBUG)

	RELAY_PIN = 4
	LOOPBACK_PIN = 17

	logging.info("Setting up pins")
	GPIO.setmode(GPIO.BCM)
	relay = Relay(RELAY_PIN)
	GPIO.setup(LOOPBACK_PIN, GPIO.IN)

	try:
		logging.info("Testing output HIGH")
		relay.enable()
		assert GPIO.input(LOOPBACK_PIN)

		sleep(1)

		logging.info("Testing output LOW")
		relay.disable()
		assert not GPIO.input(LOOPBACK_PIN)

	except KeyboardInterrupt:
		logging.info("KeyboardIntterup, shutting down GPIO...")
		raise

	except:
		logging.exception("Some exception")
		raise

	finally:
		logging.info("Cleaning up")
		relay.cleanup()
		GPIO.cleanup(LOOPBACK_PIN)

	return


if __name__ == '__main__':
	test_relay()

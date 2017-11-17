import sys
import os
sys.path.append(os.path.join("/".join(os.path.realpath(__file__).split('/')[:-2]), 'library'))
from sensor_thermocouple import Thermocouple
import timeit
import logging


def test_thermocouple():
	logging.getLogger().setLevel(logging.DEBUG)

	# test settings
	units = 'c'
	THERM_CS_PIN = 22
	therm = Thermocouple(THERM_CS_PIN)
	sampleRate = 0.1

	lasttime = 0

	try:
		logging.info("Printing thermocouple data")

		i = 0
		while i < 5:

			time = float(timeit.default_timer())
			deltatime = time - lasttime

			if deltatime >= sampleRate:
				therm.read()

				if units == 'c':
					assert therm.celcius > 0
					logging.info("{:08}C, {:010}C".format(therm.celcius, therm.itemp))
				elif units == 'f':
					itempFahrenheit = therm.itemp * 9.0 / 5.0 + 32.0
					assert itempFahrenheit > 0
					logging.info("{:08}F, {:010}F".format(therm.fahrenheit, itempFahrenheit))

				lasttime = time
				i += 1

	except KeyboardInterrupt:
		logging.info("KeyboardInterrupt, shutting down GPIO and SPI...")
		raise

	except:
		logging.exception("Some exception")
		raise

	finally:
		therm.cleanup()

	return

if __name__ == '__main__':
	test_thermocouple()
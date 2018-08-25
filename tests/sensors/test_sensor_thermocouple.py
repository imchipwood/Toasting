import pytest

from library.sensors.sensor_thermocouple import Thermocouple, TCNoTCError, TCGndShortError, TCVccShortError, TCError


def setup_module(module):
	return


def teardown_module(module):
	return


def setup_function(function):
	return


def teardown_function(function):
	return


def test_ByteListToInteger():
	tests = {
		0: [0, 0, 0, 0],
		16: [0, 0, 0, 16],
		511: [0, 0, 1, 255],
		252645135: [15, 15, 15, 15]
	}
	for expected, bytes in tests.items():
		assert Thermocouple.ByteListToInteger(bytes) == expected


def test_ConvertCelciusToFahrenheit():
	tests = {
		0: 32,
		50: 122,
		75.5: 167.9,
		100: 212
	}
	for celcius, fahrenheit in tests.items():
		assert Thermocouple.ConvertCelciusToFahrenheit(celcius) == fahrenheit


def test_CheckSPIReadForErrors():
	tests = {
		0x10001: TCNoTCError,
		0x31113: TCNoTCError,
		0x10006: TCGndShortError,
		0x50004: TCVccShortError,
		0x30008: TCError,
		0x30009: TCNoTCError,
	}
	for val, expectedException in tests.items():
		try:
			Thermocouple.CheckSPIReadForErrors(val)
		except expectedException:
			assert True
		except Exception as e:
			assert False, "{}: Expected {}, got {}".format(hex(val), str(expectedException), str(e))


def test_CalculateReferenceTemperature():
	tests = {
		0x7F0 << 4: 127,
		0x649 << 4: 100.5625,
		0x190 << 4: 25,
		0x000 << 4: 0,
		0xFFF << 4: -0.0625,
		0xFF0 << 4: -1,
		0xEC0 << 4: -20,
		0xC90 << 4: -55,
	}
	for spiReadValue, expectedCelcius in tests.items():
		print("Checking {} converts to {}".format(hex(spiReadValue), expectedCelcius))
		assert expectedCelcius == Thermocouple.CalculateReferenceTemperature(spiReadValue)
	print("\n")


def test_CalculateThermocoupleTemperature():
	tests = {
		0x1900 << 18: 1600,
		0x0FA0 << 18: 1000,
		0x0193 << 18: 100.75,
		0x0064 << 18: 25,
		0x0000 << 18: 0,
		0x3FFF << 18: -0.25,
		0x3FFC << 18: -1,
		0x3C18 << 18: -250,
	}
	for spiReadValue, expectedCelcius in tests.items():
		print("Checking {} converts to {}".format(hex(spiReadValue), expectedCelcius))
		assert expectedCelcius == Thermocouple.CalculateThermocoupleTemperature(spiReadValue)
	print("\n")


def test_Thermocouple():
	"""
	Checking for no exceptions
	"""
	tc = Thermocouple()
	assert isinstance(tc.read(), (float, int))
	assert isinstance(tc.temperature, (float, int))
	tc.cleanup()

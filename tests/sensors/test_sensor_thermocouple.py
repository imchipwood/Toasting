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


@pytest.mark.parametrize("bytes_list, expected", [
	([0, 0, 0, 0], 0),
	([0, 0, 0, 16], 16),
	([0, 0, 1, 255], 511),
	([15, 15, 15, 15], 252645135),
])
def test_ByteListToInteger(bytes_list, expected):
	"""
	Test conversion of a list of bytes to a full integer
	"""
	assert Thermocouple.ByteListToInteger(bytes_list) == expected


@pytest.mark.parametrize("celsius, fahrenheit", [
	(0, 32),
	(50, 122),
	(75.5, 167.9),
	(100, 212)
])
def test_ConvertCelsiusToFahrenheit(celsius, fahrenheit):
	"""
	Test the simple Celsius to Fahrenheit conversion
	"""
	assert Thermocouple.ConvertCelsiusToFahrenheit(celsius) == fahrenheit


@pytest.mark.parametrize("code, expectedException", [
	(0x10001, TCNoTCError),
	(0x31113, TCNoTCError),
	(0x10006, TCGndShortError),
	(0x50004, TCVccShortError),
	(0x60008, TCError),
	(0x30009, TCNoTCError),
])
def test_CheckSPIReadForErrors(code, expectedException):
	"""
	Test that errors in the values raise exceptions properly
	Test inputs derived from MAX31855 datasheet
	"""
	try:
		Thermocouple.CheckSPIReadForErrors(code)
	except expectedException:
		assert True
	except Exception as e:
		assert False, "{}: Expected {}, got {}".format(hex(code), str(expectedException), str(e))


@pytest.mark.parametrize("spi_read_value, expected_celsius", [
	(0x7F0 << 4, 127),
	(0x649 << 4, 100.5625),
	(0x190 << 4, 25),
	(0x000 << 4, 0),
	(0xFFF << 4, -0.0625),
	(0xFF0 << 4, -1),
	(0xEC0 << 4, -20),
	(0xC90 << 4, -55),
])
def test_CalculateReferenceTemperature(spi_read_value, expected_celsius):
	"""
	Test calculation of reference temperature
	Test inputs derived from MAX31855 datasheet
	"""
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
	assert expected_celsius == Thermocouple.CalculateReferenceTemperature(spi_read_value)


@pytest.mark.parametrize("spi_read_value, expected_celsius", [
	(0x1900 << 18, 1600),
	(0x0FA0 << 18, 1000),
	(0x0193 << 18, 100.75),
	(0x0064 << 18, 25),
	(0x0000 << 18, 0),
	(0x3FFF << 18, -0.25),
	(0x3FFC << 18, -1),
	(0x3C18 << 18, -250),
])
def test_CalculateThermocoupleTemperature(spi_read_value, expected_celsius):
	"""
	Test calculation of thermocouple temperature
	Test inputs derived from MAX31855 datasheet
	"""
	assert expected_celsius == Thermocouple.CalculateThermocoupleTemperature(spi_read_value)


def test_Thermocouple():
	"""
	Test that instantiating a thermocouple raises no exceptions
	"""
	tc = Thermocouple()
	assert isinstance(tc.read(), (float, int))
	assert isinstance(tc.temperature, (float, int))
	assert isinstance(tc.refTemperature, (float, int))
	tc.cleanup()


def test_csPin():
	"""
	Test that setting the CS pin works as intended
	"""
	tc = Thermocouple()
	assert tc.csPin == 0
	tc.csPin = 1
	assert tc.csPin == 1
	with pytest.raises(Exception):
		# "Expected exception for invalid CS pin"
		tc.csPin = 10

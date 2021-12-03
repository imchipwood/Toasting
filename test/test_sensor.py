import logging
import pytest
import pytest_mock

from src import IS_RASPBERRY_PI
from src.controller.sensor.binary_sensor import BinarySensorInput, BinarySensorOutput, GPIO

GPIO_OUTPUT_PIN = 17
GPIO_INPUT_PIN = 22
GPIO_OUTPUT_SETUP = False
MOCK_GPIO_STATE = None  # type: int | None


@pytest.fixture
def mock_gpio_write(mocker: pytest_mock.MockerFixture):
    def mock_write(direction: int):
        global MOCK_GPIO_STATE
        MOCK_GPIO_STATE = int(direction)

    mocker.patch("src.controller.sensor.binary_sensor.BinarySensorOutput.write", side_effect=mock_write)


@pytest.fixture
def mock_gpio_read(mocker: pytest_mock.MockerFixture):
    def mock_read(*args, **kwargs) -> int:
        global MOCK_GPIO_STATE
        return MOCK_GPIO_STATE

    mocker.patch("src.controller.sensor.binary_sensor.BinarySensorInput.read", side_effect=mock_read)


@pytest.fixture
def mock_gpio_read_with_write(mocker: pytest_mock.MockerFixture):
    global GPIO_OUTPUT_SETUP

    def mock_read(pin: int) -> int:
        global MOCK_GPIO_STATE
        GPIO.output(GPIO_OUTPUT_PIN if IS_RASPBERRY_PI else pin, MOCK_GPIO_STATE)
        return GPIO.input(pin)

    if IS_RASPBERRY_PI and not GPIO_OUTPUT_SETUP:
        GPIO_OUTPUT_SETUP = True
        GPIO.setup(GPIO_OUTPUT_PIN, GPIO.OUT)
    mocker.patch("src.controller.sensor.binary_sensor.BinarySensorInput.read", mock_read)
    # mocker.patch("Mock.GPIO.input", mock_read)


# @pytest.mark.usefixtures("mock_gpio_write")
class TestBinarySensorOutput:

    def test_sensor_write(self):
        global MOCK_GPIO_STATE
        sensor = BinarySensorOutput(GPIO_OUTPUT_PIN, True, False, logging.INFO)

        try:
            assert sensor.pin == GPIO_OUTPUT_PIN

            sensor.on()
            assert GPIO.input(sensor.pin) == GPIO.HIGH

            sensor.off()
            assert GPIO.input(sensor.pin) == GPIO.LOW
        finally:
            sensor.cleanup()

    def test_sensor_active_direction(self):
        global MOCK_GPIO_STATE
        sensor = BinarySensorOutput(GPIO_OUTPUT_PIN, True, False, logging.INFO)

        try:
            sensor.active_high = True
            sensor.on()
            assert GPIO.input(sensor.pin) == GPIO.HIGH
            sensor.off()
            assert GPIO.input(sensor.pin) == GPIO.LOW

            sensor.active_high = False
            sensor.on()
            assert GPIO.input(sensor.pin) == GPIO.LOW
            sensor.off()
            assert GPIO.input(sensor.pin) == GPIO.HIGH

        finally:
            sensor.cleanup()

    def test_sensor_toggle(self):
        global MOCK_GPIO_STATE
        sensor = BinarySensorOutput(GPIO_OUTPUT_PIN, True, False, 0.1, logging_level=logging.INFO)

        try:
            sensor.active_high = True
            sensor.toggle()
            assert GPIO.input(sensor.pin) == GPIO.LOW

            sensor.active_high = False
            sensor.toggle()
            assert GPIO.input(sensor.pin) == GPIO.HIGH

        finally:
            sensor.cleanup()


# @pytest.mark.usefixtures("mock_gpio_read")
# @pytest.mark.usefixtures("mock_gpio_read_with_write")
class TestBinarySensorInput:

    def test_sensor_read(self):
        # global MOCK_GPIO_STATE
        sensor = BinarySensorInput(GPIO_INPUT_PIN, GPIO.PUD_UP, logging.INFO)
        # GPIO.setup(GPIO_OUTPUT_PIN, GPIO.OUT)
        if IS_RASPBERRY_PI:
            gpio_output_pin = GPIO_OUTPUT_PIN
            GPIO.setup(GPIO_OUTPUT_PIN, GPIO.OUT)
        else:
            gpio_output_pin = GPIO_INPUT_PIN


        try:
            GPIO.output(gpio_output_pin, GPIO.HIGH)
            assert GPIO.HIGH == sensor.read()

            GPIO.output(gpio_output_pin, GPIO.LOW)
            assert GPIO.LOW == sensor.read()

        finally:
            sensor.cleanup()
            if IS_RASPBERRY_PI:
                GPIO.cleanup(gpio_output_pin)

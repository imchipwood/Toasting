import logging
import pytest
import pytest_mock

from src.controller.sensor.binary_sensor import BinarySensorInput, BinarySensorOutput, GPIO

GPIO_OUTPUT_PIN = 17
GPIO_INPUT_PIN = 3
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
    def mock_read() -> int:
        global MOCK_GPIO_STATE
        GPIO.output(GPIO_OUTPUT_PIN, MOCK_GPIO_STATE)
        return GPIO.input(GPIO_INPUT_PIN)

    mocker.patch("src.controller.sensor.binary_sensor.BinarySensorInput.read", mock_read)


# def write_to_pin(pin: int, value: int):
#     GPIO.output(pin, value)


@pytest.mark.usefixtures("mock_gpio_write")
class TestBinarySensorOutput:

    def test_sensor_write(self):
        global MOCK_GPIO_STATE
        sensor = BinarySensorOutput(GPIO_OUTPUT_PIN, True, False, logging.INFO)

        try:
            assert sensor.pin == GPIO_OUTPUT_PIN

            sensor.on()
            assert MOCK_GPIO_STATE == GPIO.HIGH

            sensor.off()
            assert MOCK_GPIO_STATE == GPIO.LOW
        finally:
            sensor.cleanup()

    def test_sensor_active_direction(self):
        global MOCK_GPIO_STATE
        sensor = BinarySensorOutput(GPIO_OUTPUT_PIN, True, False, logging.INFO)

        try:
            sensor.active_high = True
            sensor.on()
            assert MOCK_GPIO_STATE == GPIO.HIGH
            sensor.off()
            assert MOCK_GPIO_STATE == GPIO.LOW

            sensor.active_high = False
            sensor.on()
            assert MOCK_GPIO_STATE == GPIO.LOW
            sensor.off()
            assert MOCK_GPIO_STATE == GPIO.HIGH

        finally:
            sensor.cleanup()

    def test_sensor_toggle(self):
        global MOCK_GPIO_STATE
        sensor = BinarySensorOutput(GPIO_OUTPUT_PIN, True, False, logging.INFO)

        try:
            sensor.active_high = True
            sensor.toggle()
            assert MOCK_GPIO_STATE == GPIO.LOW

            sensor.active_high = False
            sensor.toggle()
            assert MOCK_GPIO_STATE == GPIO.HIGH

        finally:
            sensor.cleanup()


@pytest.mark.usefixtures("mock_gpio_read")
# @pytest.mark.usefixtures("mock_gpio_read_with_write")
class TestBinarySensorInput:

    def test_sensor_read(self):
        global MOCK_GPIO_STATE
        sensor = BinarySensorInput(GPIO_INPUT_PIN, GPIO.PUD_UP, logging.INFO)

        try:
            MOCK_GPIO_STATE = 1
            value = sensor.read()
            assert value == MOCK_GPIO_STATE

            MOCK_GPIO_STATE = 0
            value = sensor.read()
            assert value == MOCK_GPIO_STATE

        finally:
            sensor.cleanup()

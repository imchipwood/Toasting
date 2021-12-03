import logging

from src import IS_RASPBERRY_PI
from src.controller.sensor.binary_sensor import BinarySensorInput, BinarySensorOutput, GPIO

GPIO_OUTPUT_PIN = 17
GPIO_INPUT_PIN = 22


class TestBinarySensorOutput:

    def test_sensor_write(self):
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


class TestBinarySensorInput:

    def test_sensor_read(self):
        sensor = BinarySensorInput(GPIO_INPUT_PIN, GPIO.PUD_UP, logging.INFO)
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

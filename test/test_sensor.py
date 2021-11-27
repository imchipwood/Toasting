import logging
import pytest

from src.controller.sensor.binary_sensor import BinarySensorInput, BinarySensorOutput, GPIO


MOCK_GPIO_STATE = None


def mock_write(direction):
    global MOCK_GPIO_STATE
    MOCK_GPIO_STATE = direction


def test_sensor_write(monkeypatch):
    global MOCK_GPIO_STATE
    sensor = BinarySensorOutput(17, True, False, logging.INFO)
    monkeypatch.setattr(sensor, "write", mock_write)

    try:
        assert sensor.pin == 17

        sensor.on()
        assert MOCK_GPIO_STATE == GPIO.HIGH

        sensor.off()
        assert MOCK_GPIO_STATE == GPIO.LOW
    finally:
        sensor.cleanup()


def test_sensor_active_direction(monkeypatch):
    global MOCK_GPIO_STATE
    sensor = BinarySensorOutput(17, True, False, logging.INFO)
    monkeypatch.setattr(sensor, "write", mock_write)

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


def test_sensor_toggle(monkeypatch):
    global MOCK_GPIO_STATE
    sensor = BinarySensorOutput(17, True, False, logging.INFO)
    monkeypatch.setattr(sensor, "write", mock_write)

    try:
        sensor.active_high = True
        sensor.toggle()
        assert MOCK_GPIO_STATE == GPIO.LOW

        sensor.active_high = False
        sensor.toggle()
        assert MOCK_GPIO_STATE == GPIO.HIGH

    finally:
        sensor.cleanup()


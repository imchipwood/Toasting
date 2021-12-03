try:
    import RPi.GPIO as GPIO
except (RuntimeError, ImportError):
    import src.controller.sensor.mock_gpio as GPIO
    import logging
    logging.warning("Failed to import RPi.GPIO - using mock GPIO library")

try:
    import spidev
except (RuntimeError, ImportError):
    import src.controller.sensor.mock_spidev as spidev
    import logging
    logging.warning("Failed to import spidev - using mock spidev library")

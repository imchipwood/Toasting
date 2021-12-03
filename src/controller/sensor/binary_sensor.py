from abc import abstractmethod
import logging
import time

from src.util import get_class_name, get_logger
from src.controller.sensor import GPIO


class BinarySensor:
    def __init__(self, pin: int):
        """
        A basic binary sensor
        @param pin: GPIO pin number
        """
        super()
        self.logger = None  # type: logging.Logger | None
        self._pin = pin
        self.state = False

    @property
    def pin(self) -> int:
        """
        @return: GPIO pin to sense
        """
        return self._pin

    @pin.setter
    def pin(self, pin: int):
        """
        Set a new GPIO pin
        @param pin: GPIO pin number
        """
        if pin != self.pin:
            self.cleanup()
            self._pin = pin
            self.init()

    @abstractmethod
    def init(self):
        """
        Initialize GPIO
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.logger.debug(f"Initialized {self}")

    def cleanup(self):
        """
        Cleanup the GPIO
        """
        try:
            GPIO.cleanup(self.pin)
            self.logger.debug(f" Cleaned up {self}")
        except:
            self.logger.exception(f"Exception during cleanup for {self}")

    def __str__(self) -> str:
        return f"{get_class_name(str(__class__))} - {self.pin:>2}:{self.state!r:<5}"


class BinarySensorOutput(BinarySensor):
    def __init__(self, pin: int, active_high: bool = True, starting_state: bool = False, toggle_duration: float = 1.0,
                 logging_level: int = logging.INFO):
        """

        @param pin: GPIO pin number
        @param active_high: whether or not GPIO is active high
        @param starting_state: whether or not to turn the GPIO on at init
        @param toggle_duration: duration to hold "on" during toggle
        @param logging_level: logging level
        """
        super().__init__(pin)
        self.logger = get_logger(get_class_name(str(__class__)), logging_level)

        self.active_high = active_high
        self._toggle_duration = toggle_duration

        self.starting_state = starting_state

        self.init(self.starting_state)

    @property
    def toggle_duration(self) -> float:
        return self._toggle_duration

    def on(self):
        """
        Set the output "on"
        """
        self.write(self.active_high)
        self.state = True

    def off(self):
        """
        Set the output "off"
        """
        self.write(not self.active_high)
        self.state = False

    def write(self, output: int):
        """
        Write to the GPIO pin
        @param output: value to write
        """
        GPIO.output(self.pin, output)

    def toggle(self):
        """
        Toggle the GPIO output
        """
        self.off()
        self._wait_toggle_duration()
        self.on()
        self._wait_toggle_duration()
        self.off()

    def _wait_toggle_duration(self):
        """
        Wait the toggle duration
        """
        start_time = time.time()
        while time.time() - start_time < self.toggle_duration:
            time.sleep(0.01)

    def init(self, starting_state: bool = False):
        """
        Initialize GPIO
        @param starting_state: whether or not to turn GPIO on
        """
        super().init()
        self.starting_state = starting_state
        if self.starting_state:
            self.on()
        else:
            self.off()

    def __str__(self) -> str:
        return f"{get_class_name(__class__)} - {self.pin:>2}:{self.state!r:<5} (active high: {self.active_high!r:<5}" \
               f", starting state: {self.starting_state!r:<5})"


class BinarySensorInput(BinarySensor):
    def __init__(self, pin: int, pull_up_down: int = GPIO.PUD_UP, logging_level: int = logging.INFO):
        """
        Initialize the sensor
        @param pin: GPIO pin number
        @param pull_up_down: pull-up resistor config - pull UP or DOWN
        @param logging_level: logging level
        """
        super().__init__(pin)
        self.logger = get_logger(get_class_name(str(__class__)), logging_level)
        self.pull_up_down = pull_up_down
        self.init()

    def init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, self.pull_up_down)
        self.read()
        self.logger.debug(f"Initialized {self}")

    def read(self) -> int:
        """
        Read the GPIO as an input
        @return: value read from GPIO
        """
        self.state = GPIO.input(self.pin)
        return self.state


if __name__ == "__main__":
    relay = BinarySensorOutput(3, True, False, logging_level=logging.DEBUG)
    relay.cleanup()
    relay = BinarySensorOutput(7, False, True, logging_level=logging.DEBUG)
    relay.cleanup()

    sensor = BinarySensorInput(3, logging.DEBUG)
    for _ in range(10):
        sensor.logger.info(sensor.read())
    sensor.cleanup()

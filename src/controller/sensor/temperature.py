from abc import abstractmethod
import logging
from typing import List
from src.util import get_logger, get_class_name

try:
    import spidev
except (RuntimeError, ImportError):
    import src.controller.sensor.mock_spidev as spidev
    logging.warning("Failed to import spidev - using mock spidev library")


class Units:
    CELSIUS = "Celsius"
    FAHRENHEIT = "Fahrenheit"

    @property
    def all(self) -> List[str]:
        return [self.CELSIUS, self.FAHRENHEIT]

    def __str__(self) -> str:
        return ", ".join(self.all)


class ExceptionTemplate(Exception):
    def __call__(self, *args):
        return self.__class__(*(self.args + args))

    def __str__(self):
        return ': '.join(self.args)


class TCNoTCError(ExceptionTemplate):
    pass


class TCGndShortError(ExceptionTemplate):
    pass


class TCVccShortError(ExceptionTemplate):
    pass


class TCError(ExceptionTemplate):
    pass


class SensorTemperature:
    def __init__(self, units: str = Units.CELSIUS):
        super()

        # always store temperature in celsius
        self._temperature = 0.0
        self._units = units

        self._is_celsius = self.units == Units.CELSIUS

    @property
    def temperature(self) -> float:
        return self._temperature if self._is_celsius else self.fahrenheit

    @temperature.setter
    def temperature(self, temperature: float):
        self._temperature = temperature

    @property
    def celsius(self) -> float:
        return self._temperature

    @property
    def fahrenheit(self) -> float:
        return self._temperature * 9. / 5. + 32

    @property
    def units(self) -> str:
        return self._units

    @units.setter
    def units(self, units: str):
        if units in Units.all:
            self._units = units
        else:
            raise Exception(f"Invalid units {units}, valid values are {Units}")

    @property
    def units_short(self) -> str:
        return "C" if self._is_celsius else "F"

    @abstractmethod
    def init(self):
        raise NotImplementedError()

    @abstractmethod
    def cleanup(self):
        raise NotImplementedError()

    @abstractmethod
    def read(self) -> float:
        """
        read the sensor
        @return: temperature read
        """
        raise NotImplementedError()


class Thermocouple(SensorTemperature):
    def __init__(self, cs_pin: int = 0, units: str = Units.CELSIUS, logging_level: int = logging.INFO):
        """
        Create a Thermocouple object
        @param cs_pin: target SPI CS (chip-select) pin
        @param units: display format
        @param logging_level: logging level
        """
        super().__init__(units)
        self.logger = get_logger(get_class_name(str(__class__)), logging_level)

        self._spi = None  # type: spidev.SpiDev
        self._cs_pin = -1

        self._reference_temperature = 0.0

        # Use the property setter to initialize
        self.cs_pin = cs_pin

    @property
    def reference_temperature(self) -> float:
        return self._reference_temperature

    @property
    def cs_pin(self) -> int:
        """
        Get the CS pin number
        """
        return self._cs_pin

    @cs_pin.setter
    def cs_pin(self, cs_pin: int):
        """
        Set CS pin - reinitialize if needed
        @param cs_pin: pin number
        """
        if cs_pin not in [0, 1]:
            raise Exception("SPI CS pin must be 0 or 1")

        # Check if pin changed
        if cs_pin == self.cs_pin:
            # No change - no need to re-initialize
            return

        # Pin is valid and changed - close SPI, setup new pin, initialize SPI
        self.cleanup()
        self._cs_pin = cs_pin
        self.init()

    def init(self):
        """
        Initialize the SPI interface
        """
        self._spi = spidev.SpiDev()
        # RPi has a single SPI bus (bus 0) and two CS pins (0 or 1)
        self._spi.open(bus=0, device=self.cs_pin)

        # Set SPI CLK frequency to 4MHz (MAX31855 has max speed of 5MHz)
        self._spi.max_speed_hz = 4000000

        # Set CS active LOW
        self._spi.cshigh = False

        # Set to 8 bits per word
        self._spi.bits_per_word = 8

        # CPOL = 0 -> clock default low, thus CPHA = 0 -> capture on rising edge
        # CPOL|CPHA 0b00 = 0, 0b11 = 3
        self._spi.lsbfirst = False
        self._spi.mode = 0

    def cleanup(self):
        """
        Clean up the SPI interface
        """
        try:
            if self._spi:
                self._spi.close()
                self.logger.debug(f"SPI shut down for {self}")
        except:
            self.logger.exception(f"Exception during SPI cleanup for {self}")

    def read(self) -> float:
        """
        Perform an SPI read of the thermocouple
        @return: temperature read
        """
        values = [0] * 4
        try:
            values = self._spi.xfer(values)
        except:
            self.logger.exception(f"Exception during SPI transfer for {self}")
            raise

        string_value = ""
        for value in values:
            # store the value in base 16 and strip off leading chars
            hex_value = f"{value:02x}"
            string_value += hex_value
        value = int(string_value, 16)

        if (value & 0x0001) and (value & 0x10000):
            raise TCNoTCError('no thermocouple attached')
        if (value & 0x0002) and (value & 0x10000):
            raise TCGndShortError('short to ground')
        if (value & 0x0004) and (value & 0x10000):
            raise TCVccShortError('short to vcc')
        if value & 0x20008:
            raise TCError('dummy 0 bits missing')

        # internal MAX31855 temperature
        internal_value = value
        # remove fault bits
        internal_value >>= 4
        # pull off bottom 11 bits
        internal_value_temp = internal_value & 0x7FF
        # check sign bit and switch if necessary
        if internal_value & 0x800:
            internal_value_temp *= -1.0

        # LSB = 2^(-4) (0.0625 degrees Celsius)
        internal_value_temp *= 0.0625
        self._reference_temperature = internal_value_temp

        # thermocouple temperature
        # shift out bottom 18 bits, leaving only 14 bit thermocouple data
        value >>= 18
        # pull off bottom 13 bits
        temperature_celsius = value & 0x3FFF
        # check sign bit and switch if necessary
        if value & 0x2000:
            temperature_celsius |= 0xC000

        # LSB = 2^(-2) (0.25 degrees Celsius)
        temperature_celsius *= 0.25

        self._temperature = temperature_celsius
        return self.temperature

    def __str__(self) -> str:
        return f"{get_class_name(__class__)} - {self.cs_pin}: {self.temperature:5.2f}{self.units_short}, " \
               f"{self.reference_temperature}{self.units_short}"


if __name__ == "__main__":
    tc = Thermocouple(0, Units.CELSIUS, logging.DEBUG)
    for _ in range(10):
        try:
            value = tc.read()
            tc.logger.debug(value)
        except:
            # tc.logger.info("failed to read")
            pass
        # tc.logger.debug(tc)
    tc.cleanup()

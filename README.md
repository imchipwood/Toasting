## USE THIS PROGRAM AT YOUR OWN RISK
This tool is designed to turn a toaster oven on and off - this involves rewiring a toaster
oven and working with AC mains power. Be VERY careful and do your testing in a safe place
where an accidental fire is containable.

## Toasting - What is it?
'Toasting' is a reflow soldering toaster oven controller GUI designed for the Raspberry Pi.
Reflow soldering is generally used for small, surface mount components that are difficult
to solder by hand.

A [PID controller](https://en.wikipedia.org/wiki/PID_controller) is used to turn a relay 
on and off to maintain the target temperatures, which are measured via thermocouple.

Toasting works well on a Pi 3, but is very slow on the single-core Pi Zero. 
The Pi Zero *can* run the GUI but the live graph does not update in real time.
No other Pi models have been tested.

## Setup
Python3.5.3 was used to develop Toasting, it should work on newer versions as well. 

Note: this GUI requires wxpython-4.0.0b2, which is only available via building & installing from source.

##### Create & activate Python virtual environment
python3 -m venv toasting_venv

source toasting_venv/bin/activate

##### Install the basic Python packages
pip install -r requirements.txt

##### wxpython-4.0.0b2 - follow instructions here
https://wiki.wxpython.org/BuildWxPythonOnRaspberryPi

## Control & Sensors
####Oven Control - Relay
This application is designed to switch a toaster oven on/off via a relay. 
Ensure the relay you use is rated high enough for the power needs of your toaster oven.
Monitor the relay's temperature while running - it shouldn't get hot.

Note: Raspberry Pi GPIO are not capable of switching large relays,
so a [transistor-relay driver](http://www.electronics-tutorials.ws/blog/relay-switch-circuit.html) 
should be used.

######Default Relay pin: GPIO4 (BCM)

####Temperature Monitoring - Thermocouple
A [MAX31855 Thermocouple Amplifier](https://www.adafruit.com/product/269) is used to 
measure temperature via thermocouple. 
Communication with the MAX31855 is done via SPI. 
[Adafruit has a good tutorial on thermocouples](https://learn.adafruit.com/thermocouple?view=all)

######Default SPI CS pin: SPI0_CE0_N (GPIO8 BCM) 

## Source the venv & run application
source /path/to/toasting_venv/bin/activate

python toasting.py

## Screenshots
#### Reflow profile configuration
![Reflow Profile Configuration](https://github.com/imchipwood/Toasting/blob/master/doc/panel_reflow_configuration.png?raw=true)

#### PID tuning & other parameters
![PID Tuning & Other Parameters](https://github.com/imchipwood/Toasting/blob/master/doc/panel_tuning.png?raw=true)

#### Live graph updates during reflow
![Live Graph Screenshot](https://raw.githubusercontent.com/imchipwood/Toasting/master/doc/panel_toasting.png)
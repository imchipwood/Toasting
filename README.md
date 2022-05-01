# USE THIS PROGRAM AT YOUR OWN RISK

This tool is designed to turn a toaster oven on and off - this involves rewiring a toaster
oven and working with AC mains power. Be VERY careful and do your testing in a safe place
where an accidental fire is containable.

# Toasting - What is it?

'Toasting' is a reflow soldering toaster oven controller GUI designed for the Raspberry Pi.
Reflow soldering is generally used for small, surface mount components that are difficult
(or at least tedious) to solder by hand

![Live Graph Screenshot](https://raw.githubusercontent.com/imchipwood/Toasting/master/doc/panel_toasting.png)

A [PID controller](https://en.wikipedia.org/wiki/PID_controller) is used to turn a relay 
on and off to maintain the target temperatures, which are measured via thermocouple.

Toasting works well on a Pi 3, but is very slow on the single-core Pi Zero. 
The Pi Zero *can* run the GUI but the live graph does not update in real time.
No other Pi models have been tested.

# Setup

Originally developed for Python 3.5.3, but known to work on versions up to 3.9. 
Should work on anything >= 3.5, really.

## Create & activate Python virtual environment (Optional)

Using a virtual environment is not necessary but is recommended.

```
python3 -m venv toasting_venv
source toasting_venv/bin/activate
```

## Install Python packages available via pip

```
pip3 install -r requirements.txt
```

### wxpython

Toasting's GUI is designed using wxPython. [wxFormBuilder](https://github.com/wxFormBuilder/wxFormBuilder) 
was used to design the layout - open [ToastingGUI.fbp](/library/ui/ToastingGUI.fbp) to view/edit the layout. 
After editing, make sure to hit the "generate code" button to rebuild [ToastingGUIBase.py](/library/ui/ToastingGUIBase.py).

The current design uses `wxPython==4.1.1` - there is a wheel of this version available for armv7 devices, 
so there is no longer a need to compile wxPython manually!

# Control & Sensors

## Oven Control - Relay
This application is designed to switch a toaster oven on/off via a relay. 
Ensure the relay you use is rated high enough for the power needs of your toaster oven.
Monitor the relay's temperature while running - it shouldn't get hot.

__Note:__ Raspberry Pi GPIO are not capable of switching large relays,
so a [transistor-relay driver](http://www.electronics-tutorials.ws/blog/relay-switch-circuit.html) 
should be used.

__Default Relay pin: BCM GPIO4__

## Temperature Monitoring - Thermocouple
A [MAX31855 Thermocouple Amplifier](https://www.adafruit.com/product/269) is used to 
measure temperature via thermocouple. 
Communication with the MAX31855 is done via SPI. 
[Adafruit has a good tutorial on thermocouples](https://learn.adafruit.com/thermocouple?view=all)

__Default Thermocouple SPI CS pin: SPI0_CE0_N (BCM GPIO8)__ 

# Running Toasting
Toasting is a GUI and thus requires a desktop - set up a VNC server and connect to it, 
or connect a monitor, keyboard, and mouse.

If you're using a virtual environment, source it now.
```
python3 /path/to/Toasting/toasting.py
```

# Screenshots
#### Reflow profile configuration
![Reflow Profile Configuration](https://github.com/imchipwood/Toasting/blob/master/doc/panel_reflow_configuration.png?raw=true)

#### PID tuning & other parameters
![PID Tuning & Other Parameters](https://github.com/imchipwood/Toasting/blob/master/doc/panel_tuning.png?raw=true)

#### Live graph updates during reflow
![Live Graph Screenshot](https://raw.githubusercontent.com/imchipwood/Toasting/master/doc/panel_toasting.png)

# Basic Tool Usage
## Basic Reflow Profile Configuration
The basic configuration is designed for solder paste that reflows around 230 degrees celsius.
Stages:
- ramp2soak - Ramp temperature to 150*C
- preheat - Hold @ 150*C for 60 seconds to ensure all components have heated up
- ramp2reflow - Ramp temperature to 235*C
- reflow - Hold temperature @ 235*C for 30 seconds
- cool - Cool down. There is really no control over cooling, as the oven will hold heat for quite some time even 
with the heating elements turned off. Opening the door helps, a small USB fan helps more.  

### Editing the configuration
The basic config is located here: `Toasting/config/baseConfig.json`. The state durations & target temperatures can be
edited in the GUI. If you want to add more states, you must add them to the JSON config file.

## Tuning
The basic PID tuning should work well enough for most toaster ovens. You can edit the tuning in the JSON file, or on 
the tuning page in the GUI.

## Testing
At all times, the current temperature & reference temperatures are displayed at the top of the GUI. You may change the
display units with the buttons in the top left. 

To test the relay, go to the "Toasting" page and click the "Test Relay" button. This will toggle the relay on/off 5 times.

## Running the reflow profile
If you are satisfied with your profile & tuning, go to the "Toasting" page and click "Start Reflow". The graph will 
update in real time.

| Line Color | Description                                                                |
|------------|----------------------------------------------------------------------------|
| Orange | Target temperature (only changes when transitioning between reflow states) |
| Red | Live temperature - temperature is increasing                              | 
| Green | Live temperature - temperature is holding steady                           |
| Blue | Live temperature - temperature is decreasing                               |

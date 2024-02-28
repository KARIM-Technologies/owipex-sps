UPBoardController Python Library Documentation
Introduction
The UPBoardRGB Python library provides an interface for controlling RGB LEDs and reading switch input on the UP Board Squared Pro. This library uses the python-periphery module for GPIO interactions, making it suitable for UP Board GPIO configurations.

Installation
Install the pinctrl-upboard driver for UP Board GPIO access.
Install the python-periphery library using pip:
bash
Copy code
pip3 install python-periphery
Class: UPBoardController
Purpose: To control RGB LEDs and read switch inputs.
Initialization: Sets up GPIO pins for LEDs and the switch.
Methods
set_led(color, state):

Purpose: Turn an LED on or off.
Parameters:
color: String, the color of the LED ('R', 'G', 'B').
state: Boolean, True for on, False for off.
blink_led(color, blink_rate, duration=None):

Purpose: Blink an LED at a specified rate.
Parameters:
color: String, the color of the LED.
blink_rate: Float, time in seconds for one blink cycle.
duration: Float (optional), total duration of blinking.
display_state(state):

Purpose: Display a predefined state using LED patterns.
Parameters:
state: String, the name of the state to display.
read_switch_duration():

Purpose: Measure the duration of a switch press.
Returns: Float, duration in seconds.
cleanup():

Purpose: Clean up GPIO pins.
Usage
Import and instantiate UPBoardController in your Python script. Use the provided methods to control LEDs and read switch input.

Customization
You can modify the class to add more LED colors, states, or additional GPIO functionality.
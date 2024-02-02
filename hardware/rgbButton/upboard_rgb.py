from periphery import GPIO
import time

class UPBoardRGB:
    def __init__(self):
        # Initialisierung der GPIO-Pins
        self.led_pins = {'R': 23, 'G': 12, 'B': 13}
        self.switch_pin = 25
        self.gpio_pins = {}

        # GPIO-Objekte erstellen
        for color, pin in self.led_pins.items():
            self.gpio_pins[color] = GPIO(pin, "out")
        
        self.switch_gpio = GPIO(self.switch_pin, "in")

    def set_led(self, color, state):
        # LED ein- oder ausschalten
        self.gpio_pins[color].write(state)

    def blink_led(self, color, blink_rate, duration=None):
        # LED für eine bestimmte Zeit blinken lassen
        start_time = time.time()
        while True:
            self.set_led(color, True)
            time.sleep(blink_rate)
            self.set_led(color, False)
            time.sleep(blink_rate)
            if duration and (time.time() - start_time > duration):
                break

    def display_state(self, state):
        # Zustände der Anlage anzeigen
        state_settings = {
            'ready': ('G', 'solid'),
            'running': ('B', 'solid'),
            'warning': ('Y', 'blink', 1),
            'alarm': ('R', 'blink', 0.5),
            'stopped_error': ('R', 'solid'),
            'stopped_alarm': ('O', 'solid')
        }
        color, pattern = state_settings[state][:2]

        if pattern == 'blink':
            blink_rate = state_settings[state][2]
            self.blink_led(color, blink_rate, 5)
        elif pattern == 'solid':
            self.set_led(color, True)
        else:
            self.set_led(color, False)

    def read_switch_duration(self):
        # Dauer des Schalterdrucks messen
        start_time = None
        while True:
            if self.switch_gpio.read() and start_time is None:
                start_time = time.time()
            elif not self.switch_gpio.read() and start_time is not None:
                return time.time() - start_time

    def cleanup(self):
        # GPIO-Pins säubern
        for gpio in self.gpio_pins.values():
            gpio.close()
        self.switch_gpio.close()

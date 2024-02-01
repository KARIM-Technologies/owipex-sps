import RPi.GPIO as GPIO
import time

class UPBoardRGB:
    def __init__(self):
        # Initialisierung der GPIO-Pins
        self.led_pins = {'R': 23, 'G': 12, 'B': 13}
        self.switch_pin = 25
        self.setup_gpio()

    def setup_gpio(self):
        # GPIO-Modus einstellen
        GPIO.setmode(GPIO.BCM)
        # Pins als Ausgang setzen
        for pin in self.led_pins.values():
            GPIO.setup(pin, GPIO.OUT)
        # Schalter-Pin als Eingang setzen
        GPIO.setup(self.switch_pin, GPIO.IN)

    def set_led(self, color, state):
        # LED ein- oder ausschalten
        GPIO.output(self.led_pins[color], state)

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
            'ready': ('G', True),
            'running': ('B', True),
            'warning': ('Y', 'blink', 1),
            'alarm': ('R', 'blink', 0.5),
            'stopped_error': ('R', True),
            'stopped_alarm': ('O', True)
        }
        color, pattern = state_settings[state]
        if pattern == 'blink':
            blink_rate = state_settings[state][2]
            self.blink_led(color, blink_rate, 5)
        else:
            self.set_led(color, pattern)

    def read_switch_duration(self):
        # Dauer des Schalterdrucks messen
        start_time = None
        while True:
            if GPIO.input(self.switch_pin) and start_time is None:
                start_time = time.time()
            elif not GPIO.input(self.switch_pin) and start_time is not None:
                return time.time() - start_time

    def cleanup(self):
        # GPIO-Pins säubern
        GPIO.cleanup()

# Beispiel zur Nutzung der Bibliothek
if __name__ == '__main__':
    controller = UPBoardRGB()
    try:
        while True:
            duration = controller.read_switch_duration()
            if duration:
                print(f"Schalter wurde für {duration} Sekunden gedrückt.")
                if duration < 2:
                    controller.display_state('ready')
                elif duration < 4:
                    controller.display_state('running')
                else:
                    controller.display_state('stopped_error')
    except KeyboardInterrupt:
        # Bereinigung bei Unterbrechung
        controller.cleanup()

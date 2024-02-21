import time
import threading
from periphery import GPIO



class UPBoardRGBAsync:
    def __init__(self):
        self.led_pins = {'R': 5, 'G': 6, 'B': 26}
        self.gpio_pins = {}
        self.blink_thread = None
        self.stop_blink = threading.Event()

        for color, pin in self.led_pins.items():
            self.gpio_pins[color] = GPIO(pin, "out")
            self.set_led(color, False)  # Initial ausschalten

    def set_led(self, color, state):
        # Zustand für jede Farbe setzen
        for c in color:
            self.gpio_pins[c].write(not state)

    def start_blinking(self, color_code, blink_rate=None, blink_count=999):
        if self.blink_thread is not None:
            self.stop_blinking()

        self.stop_blink.clear()
        # Übergebe None oder einen speziellen Wert für blink_rate, um dauerhaftes Leuchten zu signalisieren
        self.blink_thread = threading.Thread(target=self._blink_led, args=(color_code, blink_rate, blink_count))
        self.blink_thread.start()

    def _blink_led(self, color_code, blink_rate, blink_count):
        if blink_rate is None:  # Wenn blink_rate None ist, leuchte dauerhaft
            self.set_led(color_code, True)
            while not self.stop_blink.is_set() and blink_count == 999:
                time.sleep(0.1)  # Kurzes Schlafen, um CPU-Zeit zu sparen und auf stop-Befehl zu überprüfen
        else:
            count = 0
            while not self.stop_blink.is_set() and (blink_count == 999 or count < blink_count):
                self.set_led(color_code, True)
                time.sleep(blink_rate)
                self.set_led(color_code, False)
                time.sleep(blink_rate)
                count += 1


    def stop_blinking(self):
        if self.blink_thread is not None:
            self.stop_blink.set()
            self.blink_thread.join()
            self.blink_thread = None

    def cleanup(self):
        self.stop_blinking()
        for gpio in self.gpio_pins.values():
            gpio.close()
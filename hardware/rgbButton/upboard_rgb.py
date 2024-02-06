from periphery import GPIO
import time

class UPBoardRGB:
    def __init__(self):
        self.led_pins = {'R': 12, 'G': 13, 'B': 23}
        self.switch_pin = 25
        self.gpio_pins = {}

        for color, pin in self.led_pins.items():
            self.gpio_pins[color] = GPIO(pin, "out")
            self.gpio_pins[color].write(True)  # LEDs initial ausschalten
        
        self.switch_gpio = GPIO(self.switch_pin, "in")

        # Mapping von Buchstabenkürzeln zu LED-Kombinationen
        self.color_map = {
            'R': 'R', 'G': 'G', 'B': 'B',
            'Y': 'RG', 'C': 'GB', 'M': 'RB',
            'W': 'RGB', 'O': 'R',  # Beispiel für Orange, ähnlich Rot
            '': ''  # Ausschalten aller LEDs
        }

    def set_color(self, color_code):
        combination = self.color_map.get(color_code, '')
        for color in self.led_pins.keys():
            self.gpio_pins[color].write(not (color in combination))

    def blink_led(self, color_code, blink_rate, blink_count=999):
        count = 0
        while True:
            self.set_color(color_code)
            time.sleep(blink_rate)
            self.set_color('')  # Ausschalten
            time.sleep(blink_rate)
            
            if blink_count != 999:
                count += 1
                if count >= blink_count:
                    break


    def cleanup(self):
        for gpio in self.gpio_pins.values():
            gpio.close()
        self.switch_gpio.close()

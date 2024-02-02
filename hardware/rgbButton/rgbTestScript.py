from upboard_rgb import UPBoardRGB
import time

def test_leds(controller):
    # Testet verschiedene LED-Zustände
    print("Testing LEDs...")
    for color in ['R', 'G', 'B']:
        print(f"Setting {color} LED on...")
        controller.set_led(color, True)
        time.sleep(1)
        print(f"Setting {color} LED off...")
        controller.set_led(color, False)
        time.sleep(1)

def test_blink_led(controller):
    # Testet das Blinken der LED
    print("Blinking red LED...")
    controller.blink_led('R', 0.5, 5)

def test_display_state(controller):
    # Testet die Anzeige verschiedener Zustände
    states = ['ready', 'running', 'warning', 'alarm', 'stopped_error', 'stopped_alarm']
    for state in states:
        print(f"Displaying state: {state}")
        controller.display_state(state)
        time.sleep(5)

def test_read_switch(controller):
    # Testet das Erfassen der Schaltereingabe
    print("Press the switch...")
    duration = controller.read_switch_duration()
    print(f"Switch was pressed for {duration:.2f} seconds.")

if __name__ == "__main__":
    controller = UPBoardRGB()
    try:
        test_leds(controller)
        test_blink_led(controller)
        test_display_state(controller)
        test_read_switch(controller)
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    finally:
        controller.cleanup()
        print("GPIO cleanup done.")

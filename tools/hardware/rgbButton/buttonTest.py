from periphery import GPIO
import time  # Import des time-Moduls

# Konfiguration
switch_line = 21  # Liniennummer des Switches

def main():
    # Initialisierung des GPIO-Pins für den Switch
    switch_gpio = GPIO(switch_line, "in")

    print("Überwachung des Switch-Zustandes. Drücken Sie CTRL+C zum Beenden.")

    try:
        while True:
            # Zustand des Switches lesen
            state = switch_gpio.read()
            print("Switch-Zustand:", "Gedrückt" if not state else "Nicht gedrückt")
            # Kurze Pause, um die Ausgabe lesbar zu halten
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Überwachung beendet.")
    finally:
        switch_gpio.close()  # Ressourcen freigeben

if __name__ == "__main__":
    main()
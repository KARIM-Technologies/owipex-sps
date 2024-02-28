from UPBoardRGB import UPBoardRGB
import time

def main():
    rgb = UPBoardRGB()
    print("UPBoard RGB LED Tester")
    print("----------------------")
    print("Verfügbare Farben: R (Rot), G (Grün), B (Blau), Y (Gelb), C (Cyan), M (Magenta), W (Weiß), O (Orange)")
    print("Geben Sie 'exit' ein, um das Programm zu beenden.")

    try:
        while True:
            color_code = input("Wählen Sie eine Farbe (Buchstabenkürzel) oder 'exit': ").strip().upper()
            if color_code == 'EXIT':
                break

            if color_code not in rgb.color_map:
                print("Ungültiges Farbkürzel. Bitte versuchen Sie es erneut.")
                continue

            # Blinkintervall und Anzahl der Blinkvorgänge einstellen
            interval = float(input("Blinkintervall eingeben (0.1 für langsam bis 1 für dauerhaft, '0' für einmaliges Blinken): "))
            blink_count = int(input("Anzahl der Blinkvorgänge eingeben (999 für unendlich): "))

            # Führt den Blink- oder Leuchttest durch
            if interval == 1:  # Dauerhaftes Leuchten
                rgb.set_color(color_code)
            else:
                rgb.blink_led(color_code, interval, blink_count)

    except KeyboardInterrupt:
        print("Programm durch Benutzerabbruch beendet.")
    finally:
        rgb.cleanup()

if __name__ == "__main__":
    main()

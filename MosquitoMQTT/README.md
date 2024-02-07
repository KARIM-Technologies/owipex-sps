# Mosquitto MQTT Broker Installation und Konfiguration auf Ubuntu 22.04

Dieser Leitfaden führt Sie durch die Installation und Grundkonfiguration von Mosquitto, einem populären MQTT-Broker, auf einem Ubuntu 22.04-Rechner.

## Schritt 1: Mosquitto Installieren

Zunächst müssen Sie Mosquitto und die zugehörigen Client-Tools installieren. Öffnen Sie ein Terminal und führen Sie die folgenden Befehle aus:

1. **Repository aktualisieren:**

    ```bash
    sudo apt-get update
    ```

2. **Mosquitto installieren:**

    ```bash
    sudo apt-get install mosquitto
    ```

3. **Mosquitto Clients installieren:**

    ```bash
    sudo apt-get install mosquitto-clients
    ```

## Schritt 2: Mosquitto Konfigurieren

Mosquitto wird mit einer Standardkonfiguration installiert, die für einfache Tests und Entwicklungszwecke ausreicht. Für eine angepasste Konfiguration bearbeiten Sie die Hauptkonfigurationsdatei:

1. **Konfigurationsdatei bearbeiten:**

    Öffnen Sie die Konfigurationsdatei `/etc/mosquitto/mosquitto.conf` mit einem Texteditor Ihrer Wahl:

    ```bash
    sudo nano /etc/mosquitto/mosquitto.conf
    ```

2. **Anpassungen vornehmen:**

    In der Konfigurationsdatei können Sie verschiedene Einstellungen anpassen, wie z.B. den Port, Zugriffsbeschränkungen und die Einrichtung von TLS/SSL für sichere Verbindungen.

## Schritt 3: Mosquitto Broker Starten

Mosquitto sollte nach der Installation automatisch starten. Verwenden Sie folgende Befehle, um den Dienst zu verwalten:

- **Status überprüfen:**

    ```bash
    sudo systemctl status mosquitto
    ```

- **Dienst starten:**

    ```bash
    sudo systemctl start mosquitto
    ```

- **Dienst stoppen:**

    ```bash
    sudo systemctl stop mosquitto
    ```

- **Dienst beim Booten automatisch starten:**

    ```bash
    sudo systemctl enable mosquitto
    ```

## Schritt 4: Testen der Mosquitto Installation

Testen Sie die Installation, indem Sie einen einfachen Publisher-Subscriber-Test durchführen:

1. **Abonnieren eines Topics:** (öffnen Sie ein neues Terminalfenster)

    ```bash
    mosquitto_sub -h localhost -t testtopic
    ```

2. **Publizieren einer Nachricht auf demselben Topic:** (in einem anderen Terminalfenster)

    ```bash
    mosquitto_pub -h localhost -t testtopic -m "Hello MQTT"
    ```

Wenn die Konfiguration korrekt ist, sollten Sie die Nachricht "Hello MQTT" im Terminal des Abonnenten sehen.

---

Mit diesen Schritten haben Sie Mosquitto erfolgreich auf Ihrem Ubuntu 22.04-Rechner installiert und konfiguriert. Sie können nun mit der Verbindung Ihrer IoT-Geräte und Anwendungen mit dem MQTT-Broker beginnen.


## Mosquitto Port ändern

Wenn Thingsboard Edge bereits den Standard-MQTT-Port 1883 verwendet, müssen Sie den Port von Mosquitto auf 1884 oder einen anderen verfügbaren Port ändern. Befolgen Sie diese Schritte, um den Port zu ändern:

1. **Mosquitto Konfigurationsdatei bearbeiten:**

    Öffnen Sie die Mosquitto-Konfigurationsdatei `/etc/mosquitto/mosquitto.conf` in einem Texteditor Ihrer Wahl:

    ```bash
    sudo nano /etc/mosquitto/mosquitto.conf
    ```

2. **Port ändern:**

    Suchen Sie in der Konfigurationsdatei die Zeile, die den Port definiert. Wenn keine solche Zeile existiert, fügen Sie sie am Ende der Datei hinzu, um den Broker auf Port 1884 laufen zu lassen:

    ```
    port 1884
    ```

    Speichern und schließen Sie die Datei.

3. **Mosquitto neu starten:**

    Nachdem Sie die Konfigurationsdatei geändert haben, müssen Sie den Mosquitto-Dienst neu starten, um die Änderungen zu übernehmen:

    ```bash
    sudo systemctl restart mosquitto
    ```

4. **Firewall konfigurieren (optional):**

    Wenn auf Ihrem Server eine Firewall läuft, müssen Sie sicherstellen, dass der neue Port (in diesem Fall 1884) geöffnet ist. Verwenden Sie folgenden Befehl, um den Port in UFW (Uncomplicated Firewall) zu öffnen, falls UFW verwendet wird:

    ```bash
    sudo ufw allow 1884/tcp
    ```

    Überprüfen Sie die Firewall-Konfiguration und passen Sie sie entsprechend an, falls Sie eine andere Firewall-Lösung verwenden.

5. **Verbindung testen:**

    Testen Sie die Verbindung zum Mosquitto MQTT-Broker über den neuen Port, indem Sie `mosquitto_sub` und `mosquitto_pub` mit dem aktualisierten Port verwenden:

    - **Abonnieren eines Topics auf Port 1884:**

        ```bash
        mosquitto_sub -h localhost -t testtopic -p 1884
        ```

    - **Publizieren einer Nachricht auf demselben Topic auf Port 1884:**

        ```bash
        mosquitto_pub -h localhost -t testtopic -m "Hello MQTT on Port 1884" -p 1884
        ```

    Wenn die Konfiguration korrekt ist, sollten Sie die Nachricht "Hello MQTT on Port 1884" im Terminal des Abonnenten sehen.

Durch die Änderung des Ports können Sie Mosquitto parallel zu Thingsboard Edge betreiben, ohne Portkonflikte zu verursachen.



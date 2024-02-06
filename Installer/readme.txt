Skript ausfühbar machen
chmod +x skriptname.sh

Skript ausführen
./skriptname.sh



Im Fall das das der Service gestoppt oder deinstalliert werden muss. 

Stoppen Sie den Service: Bevor Sie den Service deinstallieren, sollten Sie ihn zuerst stoppen, um sicherzustellen, dass er nicht mehr läuft. Verwenden Sie dazu den Befehl:
sudo systemctl stop app.service

Deaktivieren Sie den Service: Deaktivieren Sie den Service, um zu verhindern, dass er beim Systemstart automatisch gestartet wird:
sudo systemctl disable app.service

Löschen Sie die Service-Datei: Die Datei app.service befindet sich normalerweise im Verzeichnis /etc/systemd/system/ oder /usr/lib/systemd/system/. Sie sollten diese Datei löschen, um den Service zu entfernen:
sudo rm /etc/systemd/system/app.service


Neuladen des systemd Daemon: Nachdem Sie die Service-Datei gelöscht haben, sollten Sie systemd neu laden, damit es die Änderungen erkennt:
sudo systemctl daemon-reload





REVERSE SSH
Auf dem Tablet (Client-Seite):
Installiere SSH: Stelle sicher, dass auf dem Tablet ein SSH-Client installiert ist. Dies hängt vom Betriebssystem des Tablets ab. Bei Android-Geräten kannst du Apps wie Termux verwenden, während bei Windows-Tablets Putty oder ähnliche Programme nützlich sind.

Öffne eine Terminal-App: Starte die Terminal-App auf deinem Tablet.

Reverse SSH-Befehl ausführen: Führe den folgenden Befehl im Terminal aus:


ssh -R 2201:localhost:22 benutzername@serveradresse
Hierbei ist:

10000: der Port auf dem Server, über den du später auf das Tablet zugreifen möchtest. Dies sollte für jedes Tablet einzigartig sein.
localhost:22: gibt an, dass der SSH-Server des Tablets auf Port 22 läuft.
benutzername: dein Benutzername auf dem Server.
serveradresse: die Adresse deines Servers.
Auf dem Server (Server-Seite):
SSH-Server betreiben: Stelle sicher, dass ein SSH-Server auf deinem Server läuft und externe Verbindungen akzeptiert.

Port-Weiterleitung erlauben: Du musst möglicherweise die SSH-Konfiguration des Servers bearbeiten, um die Port-Weiterleitung zu erlauben. Dies erfolgt in der Datei sshd_config (normalerweise unter /etc/ssh/sshd_config). Stelle sicher, dass die Zeile GatewayPorts clientspecified oder GatewayPorts yes vorhanden ist und nicht auskommentiert ist.

SSH-Server neu starten: Nachdem du Änderungen an der Konfiguration vorgenommen hast, starte den SSH-Dienst neu, um die Änderungen zu übernehmen.

Verbindung zum Tablet herstellen:
Sobald das Tablet über Reverse SSH mit dem Server verbunden ist, kannst du dich vom Server aus oder von einem anderen Gerät im gleichen Netzwerk (unter Verwendung der Serveradresse und des zugewiesenen Ports) zum Tablet verbinden. Zum Beispiel:

css
Copy code
ssh -p 1000"X" root@portal.owipex.io  #X ist die fortlaufende portnumer
Hierbei ist tabletbenutzername der Benutzername auf dem Tablet.

## 3. Klonen des Git-Repositories

Nachdem Git erfolgreich installiert und konfiguriert wurde, ist der nächste Schritt das Klonen des spezifischen Git-Repositories, das die Codebasis und Konfigurationen für unser IoT-System enthält. In diesem Fall werden wir das Repository `owipex-sps` von KARIM-Technologies klonen.

### Voraussetzungen

- Git muss auf Ihrem System installiert sein (siehe vorheriger Abschnitt).
- Eine Internetverbindung.

### Schritte zum Klonen des Repositories

1. **Öffnen Sie ein Terminal**: Navigieren Sie zum gewünschten Verzeichnis auf Ihrem Server, in dem das Repository geklont werden soll.

2. **Klonen Sie das Repository**: Verwenden Sie den folgenden Befehl, um das Repository `owipex-sps` zu klonen. Ersetzen Sie `<Zielverzeichnis>` mit dem Pfad des Verzeichnisses, in dem Sie das Repository speichern möchten, oder lassen Sie diesen Teil weg, um das Repository in einem neuen Verzeichnis mit dem Namen des Repositories zu klonen:

    ```bash
    git clone https://github.com/KARIM-Technologies/owipex-sps.git <Zielverzeichnis>
    ```

    Wenn Sie den Pfad `<Zielverzeichnis>` weglassen, erstellt Git automatisch ein neues Verzeichnis namens `owipex-sps` im aktuellen Verzeichnis und speichert dort das geklonte Repository.

3. **Wechseln Sie in das Repository-Verzeichnis**: Nachdem das Klonen abgeschlossen ist, navigieren Sie in das Verzeichnis des geklonten Repositories:

    ```bash
    cd owipex-sps
    ```

    (oder `cd <Zielverzeichnis>`, falls Sie einen spezifischen Pfad angegeben haben).

4. **Überprüfen Sie den Status**: Optional können Sie den Status des Repositories überprüfen, um sicherzustellen, dass alles korrekt geklont wurde. Führen Sie dazu folgenden Befehl aus:

    ```bash
    git status
    ```

## 4. Ausführen des Installer-Skripts

Nachdem das Repository erfolgreich geklont wurde, müssen spezifische Installationsskripte ausgeführt werden, um die Umgebung und Abhängigkeiten für unser IoT-System zu konfigurieren. Dazu gehört das Skript `auto_install.sh`, das im `Installer/scripts`-Verzeichnis des geklonten Repositories liegt.

### Voraussetzungen

- Sie haben das `owipex-sps` Repository erfolgreich geklont (siehe vorheriger Abschnitt).
- Sie haben Terminalzugriff mit den notwendigen Berechtigungen (die Ausführung einiger Skripte erfordert möglicherweise `root`-Zugriff).

### Schritte zum Ausführen des Installer-Skripts

1. **Wechseln Sie in das Skriptverzeichnis**: Navigieren Sie in das `Installer/scripts`-Verzeichnis innerhalb des geklonten `owipex-sps` Repositories:

    ```bash
    cd owipex-sps/Installer/scripts
    ```

2. **Machen Sie das Skript ausführbar**: Bevor Sie das Skript ausführen können, müssen Sie sicherstellen, dass es die notwendigen Ausführungsberechtigungen hat. Verwenden Sie den `chmod`-Befehl, um das Skript ausführbar zu machen:

    ```bash
    chmod +x auto_install.sh
    ```

3. **Versuchen Sie, das Skript auszuführen**: Wenn Sie das Skript ohne `sudo` ausführen, werden Sie möglicherweise aufgefordert, es als `root`-Benutzer auszuführen:

    ```bash
    ./auto_install.sh
    ```

    Die Ausgabe wird darauf hinweisen: "Bitte führen Sie das Skript als Root aus."

4. **Führen Sie das Skript als Root aus**: Um das Skript mit Administratorrechten auszuführen, verwenden Sie `sudo`:

    ```bash
    sudo ./auto_install.sh
    ```

    Dies startet den Installationsprozess. Folgen Sie den Anweisungen auf dem Bildschirm, um die Installation abzuschließen.

### Wichtige Hinweise

- Stellen Sie sicher, dass Sie alle erforderlichen Informationen zur Hand haben, da das Skript möglicherweise Eingaben während des Installationsprozesses anfordert.
- Überprüfen Sie nach Abschluss der Installation die Protokolle und Ausgaben, um sicherzustellen, dass alles erfolgreich installiert wurde und keine Fehler aufgetreten sind.

Mit diesen Schritten haben Sie das notwendige Installationsskript ausgeführt, um die Umgebung für Ihre IoT-Systeme einzurichten und zu konfigurieren.

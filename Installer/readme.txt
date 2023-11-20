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
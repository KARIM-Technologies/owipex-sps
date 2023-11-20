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
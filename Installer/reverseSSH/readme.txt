SSH-Schlüsselpaar erstellen
Hier ist eine Anleitung, wie du ein SSH-Schlüsselpaar erstellst und auf deinem Server einrichtest:

1. Schlüsselpaar erstellen:
Auf deinem lokalen Gerät (in diesem Fall das Tablet oder der Computer, von dem aus du den Tunnel einrichtest), führe den folgenden Befehl aus:

bash
Copy code
ssh-keygen -t rsa -b 4096
-t rsa gibt den Typ des Schlüsselpaares an (RSA).
-b 4096 legt die Länge des Schlüssels fest, hier 4096 Bits, was aktuell als sehr sicher gilt.
Während des Prozesses wirst du aufgefordert, einen Speicherort für den Schlüssel anzugeben und optional ein Passwort festzulegen. Für automatisierte Prozesse wie deinen SSH-Tunnel ist es am besten, kein Passwort zu setzen.

2. Öffentlichen Schlüssel auf den Server kopieren:
Nachdem du das Schlüsselpaar erstellt hast, musst du den öffentlichen Schlüssel (id_rsa.pub) auf deinen Server übertragen. Dies kannst du mit dem Befehl ssh-copy-id tun:

bash
Copy code
ssh-copy-id -i ~/.ssh/id_rsa.pub benutzername@serveradresse
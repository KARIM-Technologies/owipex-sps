#Start der Readme


1. Ubuntu 20.04.5 Server installieren

2. Kernel prüfen und mit UP Board Kernel updaten
    Can you run the command:
    uname -a

    and provide the full output?

    also please run and share the output of the following:
    dmesg | grep pinctrl

    https://github.com/up-board/up-community/wiki/Ubuntu_18.04#install-ubuntu-kernel-540-from-ppa-on-ubuntu-1804

    Install Ubuntu kernel 5.4.0 from PPA on Ubuntu 18.04
    This is the latest Kernel available for the UP Series. It has been validated on UP Board, UP Core, UP Squared, UP Core Plus, UP Xtreme, and UP Squared Pro.

    After the reboot you need to add our repository:

    sudo add-apt-repository ppa:up-division/5.4-upboard

    Update the repository list

    sudo apt update

    Remove all the generic installed kernel (select No on the question "Abort Kernel Removal")

    sudo apt-get autoremove --purge 'linux-.*generic'

    Install our kernel(18.04 and 20.04 share the same 5.4 kernel):

    sudo apt-get install linux-generic-hwe-18.04-5.4-upboard

    Install the updates:

    sudo apt dist-upgrade -y

    sudo update-grub

    Reboot

    sudo reboot

3. Install pin control
    https://github.com/up-division/pinctrl-upboard

    Install deb package
    Install deb package on Debian-based Linux distributions like Ubuntu, Linux Mint, Parrot....

    install DKMS
    sudo apt install dkms 

    Reboot the system before installing the pinctrl driver.
    
    Download the latest deb package from the release folder
    sudo wget https://github.com/up-division/pinctrl-upboard/releases/download/v1.1.3/pinctrl-upboard_1.1.3_all.deb


    install deb package
    sudo dpkg -i pinctrl-upboard_1.1.3_all.deb

    Reboot the system again before starting to use the 40 pin header functionalities.

4. MRAA (Ubuntu20.04)
    https://github.com/up-board/up-community/wiki/MRAA
    Teteh Camillus Chinaedu edited this page on May 31, 2022 · 7 revisions
    
    Introduction
    libmraa is a low-level library, developed by Intel, for accessing the I/O functions (GPIO, I2C, SPI, PWM, UART) on a variety of boards such as Intel's Galileo and Edison boards, MinnowBoard Max, Raspberry Pi, and more. It is written in C/C++ and provides Python and Javascript bindings. libmraa supports the UP board since (v0.9.5).

    upm is a high-level library that makes use of mraa, and provides packages/modules to manage a variety of sensors and actuators. v0.5.1.

    Setup
    Note: If using Ubuntu 18.04, for UP Xtreme please follow dedicated installation instruction in the dedicated section below

    To install and ensure that the most up-to-date version is installed, please run the following commands:

    sudo add-apt-repository ppa:mraa/mraa
    sudo apt-get update
    sudo apt-get install mraa-tools mraa-examples libmraa2 libmraa-dev libupm-dev libupm2 upm-examples
    sudo apt-get install python-mraa python3-mraa libmraa-java

5. Here some system outputs:

uname -a:
Linux lidarbox 5.4.0-1-generic #0~upboard2-Ubuntu SMP Sun Oct 25 14:06:23 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux

dmesg|grep pinctrl:
[ 0.306554] pinctrl core: initialized pinctrl subsystem

mraa-gpio version:
Version v2.0.0 on Unknown platform

mraa-gpio list
No Pins

1. Initialisieren des Codes
    .env anpassen
        #Datei umbenennen in .env
        #cp env.example .env


# Installationsdokumentation für IoT-Systeme

## 1. Installation der Linux Distribution Ubuntu Server 22.04 LTS

Um die Basis für unsere IoT-Systeme zu schaffen, beginnen wir mit der Installation von Ubuntu Server 22.04 LTS. Dieses Betriebssystem bietet langfristigen Support (LTS) und ist für die Stabilität und Sicherheit kritischer Anwendungen optimiert.

### Voraussetzungen

- Ein kompatibler Server oder eine virtuelle Maschine.
- Ein USB-Stick mit mindestens 4 GB Speicherplatz für das Installationsmedium.
- Eine Internetverbindung für den Download der Software und Updates während der Installation.

### Schritte zur Installation

1. **Ubuntu Server 22.04 LTS herunterladen**: Gehen Sie zur offiziellen Ubuntu-Website und laden Sie das ISO-Abbild für Ubuntu Server 22.04 LTS herunter. [Ubuntu Server Download](https://ubuntu.com/download/server)

2. **Bootfähiges USB-Laufwerk erstellen**: Verwenden Sie ein Tool wie Rufus oder Etcher, um das heruntergeladene ISO-Abbild auf einen USB-Stick zu übertragen und bootfähig zu machen.

3. **Von USB booten**: Stellen Sie sicher, dass der Server/virtuelle Maschine so eingestellt ist, dass von USB gebootet wird. Dies kann in den BIOS- oder UEFI-Einstellungen konfiguriert werden.

4. **Installationsprozess starten**: Folgen Sie den Anweisungen auf dem Bildschirm. Wählen Sie die gewünschte Sprache, Standort, Tastaturlayout und weitere Einstellungen.

5. **Festplattenpartitionierung**: Entscheiden Sie, ob Sie die gesamte Festplatte verwenden oder manuelle Partitionierung für erweiterte Konfigurationen vornehmen möchten.

6. **Benutzer- und Servereinstellungen**: Legen Sie den Benutzernamen, das Passwort und den Hostnamen für Ihren Server fest. Es wird empfohlen, während der Installation die Option für die automatischen Sicherheitsupdates zu aktivieren.

7. **Softwareauswahl**: Für ein minimales Setup können Sie die vorgegebenen Optionen übernehmen oder zusätzliche Softwarepakete nach Bedarf auswählen.

8. **Installation abschließen**: Nachdem alle Einstellungen konfiguriert sind, startet die Installation. Entfernen Sie nach Abschluss das USB-Laufwerk und starten Sie den Server neu.

9. **Erster Login**: Nach dem Neustart können Sie sich mit dem zuvor erstellten Benutzernamen und Passwort anmelden.

Mit diesen Schritten haben Sie erfolgreich Ubuntu Server 22.04 LTS als Grundlage für Ihre IoT-Systeme installiert.


## 2. Installation von Git

Nachdem Ubuntu Server 22.04 LTS installiert ist, ist der nächste Schritt die Installation von Git. Git ist ein unverzichtbares Werkzeug für die Versionskontrolle und wird benötigt, um unsere IoT-Systemkonfigurationen und -Code sicher zu verwalten.

### Voraussetzungen

- Ein funktionierendes Ubuntu Server 22.04 LTS System.
- Administratorrechte (in der Regel Zugriff über den Benutzer `root` oder die Möglichkeit, Befehle mit `sudo` auszuführen).

### Schritte zur Installation

1. **Paketlisten aktualisieren**: Aktualisieren Sie zuerst die Paketlisten, um sicherzustellen, dass Sie die neuesten Versionen der Software installieren. Öffnen Sie ein Terminal und führen Sie folgenden Befehl aus:

    ```bash
    sudo apt update
    ```

2. **Git installieren**: Installieren Sie Git mit dem `apt` Paketmanager durch Ausführen des folgenden Befehls:

    ```bash
    sudo apt install git -y
    ```

    Die Option `-y` bestätigt automatisch, dass Sie mit der Installation fortfahren möchten.

3. **Git-Version überprüfen**: Nach der Installation können Sie die installierte Git-Version überprüfen, um sicherzustellen, dass die Installation erfolgreich war. Führen Sie dazu folgenden Befehl aus:

    ```bash
    git --version
    ```

    Die Ausgabe sollte die installierte Git-Version anzeigen, z.B. `git version 2.XX.X`.

4. **Git konfigurieren**: Konfigurieren Sie Git mit Ihrem Namen und Ihrer E-Mail-Adresse, die in Ihren Commits verwendet werden. Ersetzen Sie `Ihr Name` und `ihre.email@example.com` mit Ihren eigenen Informationen:

    ```bash
    git config --global user.name "Ihr Name"
    git config --global user.email "ihre.email@example.com"
    ```

### Überprüfung der Git-Konfiguration

- Um die aktuelle Konfiguration zu überprüfen, können Sie folgende Befehle ausführen:

    ```bash
    git config --global user.name
    git config --global user.email
    ```

    Diese Befehle geben den Namen und die E-Mail-Adresse aus, die Sie für Git konfiguriert haben.

Mit der Installation und Konfiguration von Git ist Ihr System nun bereit für die Versionskontrolle Ihrer IoT-Projekte.

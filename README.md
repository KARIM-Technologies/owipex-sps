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

1. Initialisieren des Codes
    .env anpassen
        #Datei umbenennen in .env
        #cp env.example .env
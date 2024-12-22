#!/bin/bash

echo "Enabling and starting ssh"
sudo systemctl start ssh
sudo systemctl enable ssh

echo "Installing pigpio"
sudo apt-get install pigpio

echo "Enabling and starting pigpio"
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

echo "Installing bluez tools and pulseaudio for audio control"
sudo apt install bluetooth bluez bluez-tools rfkill pulseaudio pavucontrol

echo "Installing audio control dependencies"
sudo apt install portaudio19-dev python3-pyaudio

echo "Installing FLAC"
sudo apt install flac

pip install pip==22.3.1
python -m pip install -r requirements.txt


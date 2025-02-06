# Bird Laser Targeter on the Edge

## What is this project?

This repository stores the code for a program that uses a laser pointer and a couple of servos to scare off birds that are being menaces and flying into our homes. Hopefully what's being done here doesn't break any laws.

## Components

- [2 SG90 Servos and Pan Tilt Kit](https://sg.cytron.io/p-pan-tilt-servo-kit-for-camera-unassembled) x1
- [Laser Diode Module](https://shopee.sg/kuriosity.sg/8657033875) x1
- [Raspberry Pi Zero 2 WH](https://sg.cytron.io/p-raspberry-pi-zero-2-w)
- [ReSpeaker 2-Microphone Raspberry Pi HAT](https://sg.cytron.io/p-respeaker-2-microphone-raspberry-pi-hat)
- [CSI Camera](https://sg.cytron.io/p-5mp-camera-board-for-raspberry-pi)

## Installation on Raspberry Pi Zero 2 W

Before this project can work, you will need to install some packages used by this project.

```bash
sudo apt update
sudo apt upgrade
sudo apt install git
sudo apt install portaudio19-dev
sudo apt install python3
sudo apt install python3-pip
sudo apt-get install rpi.gpio
```

Then you can clone this repo with git. The second line renames the repo's directory to edge-project.

```bash
git clone https://github.com/dragonstonehafiz/sit-y2tri2-inf2009-edge-project.git
mv sit-y2tri2-inf2009-edge-project edge-project
cd edge-project
```

Now we will set up the virtual environment that will be used for this project.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


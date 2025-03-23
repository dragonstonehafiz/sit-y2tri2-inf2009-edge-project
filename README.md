# Bird Laser Targeter on the Edge

## **Overview**

This repository contains the code for a bird deterrence system that utilizes a laser pointer and servo motors to **scare off birds** that may fly into homes and cause disturbances. The system runs on a **Raspberry Pi Zero 2W** and features wake activation, camera-based bird detection, and laser targeting.

## **Components**

The following components are required to build this project:

- [2 SG90 Servos and Pan Tilt Kit](https://sg.cytron.io/p-pan-tilt-servo-kit-for-camera-unassembled) x1
- [Laser Diode Module](https://shopee.sg/kuriosity.sg/8657033875) x1
- [Raspberry Pi Zero 2 WH](https://sg.cytron.io/p-raspberry-pi-zero-2-w)
- [ReSpeaker 2-Microphone Raspberry Pi HAT](https://sg.cytron.io/p-respeaker-2-microphone-raspberry-pi-hat)
- [CSI Camera](https://sg.cytron.io/p-5mp-camera-board-for-raspberry-pi)

## System Design

This system is built to run on a Raspberry Pi Zero 2W using a lightweight Linux distribution. 
It integrates multiple hardware components—camera, servos, laser module, and microphone—to detect and deter birds through targeted motion and light. 
The PiCamera provides real-time video, which is processed locally or remotely using a YOLOv5 model to detect birds. 
Upon detection, servo motors orient the laser toward the target. Audio input can also trigger the system to begin scanning.

A USB microphone enables audio-based activation, while MQTT facilitates communication between the Pi and an optional remote server for processing or control. 
The system operates as a finite state machine with four main modes: IDLE, SCAN, TRACKING, and QUIT.

## Block Diagram and Control Flow

The software runs as a state machine on the Raspberry Pi, cycling between different operational states:

- **IDLE**: Waits for an audio trigger (e.g. bird chirp).
- **SCAN**: Sweeps the environment using servos while searching for a target.
- **TRACKING**: Tracks a detected bird and orients the laser accordingly.
- **QUIT**: Safely shuts down the system and disconnects all hardware.

The control flow supports two operating modes:
1. **Local Mode**: All detection and control run on the Pi using ONNX-based YOLOv5 inference.
2. **Remote Mode**: The Pi sends camera frames to a remote server over MQTT, which processes the frames and sends back control signals.

## **Installation Instructions**

### **On Raspberry Pi Zero**

#### **Step 1: Install Required Packages**

Run the following commands to update your system and install the necessary dependencies:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git 
sudo apt install -y portaudio19-dev 
sudo apt install -y python3 
sudo apt install -y python3-pip 
sudo apt install -y python3-venv
sudo apt install -y python3-rpi.gpio 
sudo apt install -y python3-picamera2 
sudo apt install -y mosquitto
sudo apt-get install -y python3-opencv
sudo apt install -y v4l-utils
```

#### **Step 2: Install Drivers for ReSpeaker Mic Hat**

```bash
git clone https://github.com/HinTak/seeed-voicecard.git
cd seeed-voicecard
git checkout v6.6
sudo ./install.sh
```

Reboot your Raspberry Pi Zero.

```bash
sudo reboot now
```

Test the microphone.

```bash
arecord -D plughw:CARD=seeed2micvoicec,DEV=0 -r 16000 -c 1 -f S16_LE -t wav -d 5 test.wav
aplay -D plughw:CARD=seeed2micvoicec,DEV=0 test.wav
```

#### **Step 3: Clone the Repository**

```bash
git clone https://github.com/dragonstonehafiz/inf2009-project.git
cd inf2009-project
```

#### **Step 4: Set Up Virtual Environment**

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt --verbose
pip install "paho-mqtt<2.0"
pip uninstall numpy
pip install --no-cache-dir numpy
pip install onnxruntime==1.16.0 --no-cache-dir
sudo apt-get -y install libopenblas-dev
```

### **(Optional) Desktop Server**

If you want to **view the camera feed remotely**, you can set up a server on a desktop.

#### **Step 1: Install Required Packages**

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git python3 python3-pip mosquitto
```

#### **Step 2: Clone the Repository**

```bash
git clone https://github.com/dragonstonehafiz/inf2009-project.git
mv inf2009-project edge-project
cd edge-project
```

#### **Step 3: Set Up Virtual Environment**

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements_server.txt
pip install "paho-mqtt<2.0"
```

## Usage

### Raspberry Pi Zero 2W 

*TODO*

### Server

Activate mosquitto server.

```bash
sudo mosquitto -c /etc/mosquitto/mosquitto.conf
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
sudo systemctl restart mosquitto
```
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

![Block Diagram](image/BlockDiagram.png)

The software runs as a state machine on the Raspberry Pi, cycling between different operational states:

- **IDLE**: Waits for an audio trigger (e.g. bird chirp).
- **SCAN**: Sweeps the environment using servos while searching for a target.
- **TRACKING**: Tracks a detected bird and orients the laser accordingly.
- **QUIT**: Safely shuts down the system and disconnects all hardware.

The control flow supports two operating modes:
1. **Local Mode**: All detection and control run on the Pi using ONNX-based YOLOv5 inference.
2. **Remote Mode**: The Pi sends camera frames to a remote server over MQTT, which processes the frames and sends back control signals.

![Control Flow](image/ControlFlow.png)

## Installation Instructions (Raspberry Pi Zero 2W)

### Requirements

- Raspberry Pi Zero 2W (running Raspberry Pi OS Lite 64-bit)
- CSI camera module (with `picamera2` support)
- 2x SG90 servo motors + Pan-Tilt kit
- Laser module (digital pin controlled)
- MQTT broker (e.g. Mosquitto, can be on local server)
- Python 3.9+

### Step 1: Update and Install System Packages

```bash
sudo apt update && sudo apt upgrade -y

# Core Python and system packages
sudo apt install -y python3 python3-pip python3-venv git
sudo apt install -y libopenblas-dev libjpeg-dev libtiff-dev
sudo apt install -y python3-opencv v4l-utils
sudo apt install -y portaudio19-dev

# Camera support
sudo apt install -y python3-picamera2

# MQTT client
sudo apt install -y mosquitto mosquitto-clients
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/dragonstonehafiz/inf2009-project.git
cd inf2009-project
```

### Step 3: Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt --verbose

# Ensure compatible versions of MQTT and ONNXRuntime
pip install "paho-mqtt<2.0"
pip install onnxruntime==1.16.0 --no-cache-dir

# Reinstall numpy cleanly
pip uninstall numpy
pip install --no-cache-dir numpy

# Reinstall this package after new numpy install
sudo apt-get -y install libopenblas-dev
```

## Installation Instructions (Desktop Server)

This setup is optional and allows you to view the PiCamera feed remotely, run bird detection on a more powerful machine, and send servo commands back to the Raspberry Pi over MQTT.

### Requirements

- Linux Desktop (Ubuntu recommended)
- Python 3.9+
- Mosquitto

### Step 1: Install System Packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
sudo apt install -y mosquitto mosquitto-clients
sudo apt install -y libopencv-dev python3-opencv
```

### Step 2: Clone the Repository

```bash
git clone https://github.com/dragonstonehafiz/inf2009-project.git
cd inf2009-project
```

### Step 3: Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements_server.txt
pip install "paho-mqtt<2.0"
pip install onnxruntime==1.16.0 --no-cache-dir
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
# Bird Laser Targeter on the Edge

## What is this project?

This repository stores the code for a program that uses a laser pointer and a couple of servos to scare off birds that are being menaces and flying into our homes. Hopefully what's being done here doesn't break any laws.

## Components

- [2 SG90 Servos and Pan Tilt Kit](https://sg.cytron.io/p-pan-tilt-servo-kit-for-camera-unassembled) x1
- [Laser Diode Module](https://shopee.sg/kuriosity.sg/8657033875) x1
- [Arduino UNO R3](https://shopee.sg/kuriosity.sg/27759981980) x1
- [Raspberry Pi 5](https://sg.cytron.io/p-raspberry-pi-5)
- [ESP32-CAM with MB Programmer](https://shopee.sg/kuriosity.sg/8557052439)
- Wires + Breadboard + Breadboard Power Module
- Any USB webcam (for testing)

## Installation on Raspberry Pi 5.

You need to install git to clone this repository.

```bash
sudo apt update
sudo apt upgrade
sudo apt install git
```

Then you can clone this repo.

```bash
git clone https://github.com/dragonstonehafiz/sit-y2tri2-inf2009-edge-project.git
```

Next, we will set up the virtual environment used for this program.

```bash
cd dragonstonehafiz/sit-y2tri2-inf2009-edge-project.git
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Testing a controller and mouse object detection model

Before we can test a model, we need to change permissions on the downloaded eim file.

```bash
chmod +x model/test-image-linux-aarch64-v9.eim
```

Connect your USB webcam and run the code below. What this does is run the python script `TEST_Eim.py` in the code_python folder. The script takes the image captured by the webcam and splits it into two, performing object detection on the left side of the image and the right side of the image. If it is able to detect an object, it will print data to the terminal. 

**NOTE**: The model used in this script is `model/test-image-linux-aarch64-v9.eim` which is trained to detect video game controllers and computer mice.

Expected output:

```
RIGHT: Found 0 bounding boxes (76 ms.)
LEFT: Found 0 bounding boxes (84 ms.)
RIGHT: Found 0 bounding boxes (76 ms.)
LEFT: Found 0 bounding boxes (82 ms.)
RIGHT: Found 1 bounding boxes (76 ms.)
        controller (0.67): x=236 y=277 w=70 h=42
LEFT: Found 0 bounding boxes (85 ms.)
RIGHT: Found 2 bounding boxes (76 ms.)
        mouse (0.83): x=223 y=111 w=36 h=8
        mouse (0.73): x=171 y=220 w=103 h=68
```

```bash
python code_python/TEST_Eim.py
```

What 
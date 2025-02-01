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

## Installation on Raspberry Pi 5

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

## Testing a controller model trained on Edge Impulse

Before we can test a model, we need to change permissions on the downloaded eim file.

```bash
chmod +x model/test-image-linux-aarch64-v9.eim
```

Connect your USB webcam and run the code below. What this does is run the python script `TEST_EimBoundingBoxes.py` in the code_python folder. The script looks at each frame recorded by the webcam and runs inference using the `test-image-linux-aarch64-v9.eim` model. However, it ignores classifications that are for 'mouse', and only considers bounding boxes with confidence scores larger than 0.95. It then tracks the bounding box with the largest confidence score and renders it as an overlay.

```bash
python code_python/TEST_EimBoundingBoxes.py
```

**NOTE**: The model used in this script is `model/test-image-linux-aarch64-v9.eim` which is trained to detect video game controllers and computer mice.

Expected output:
![Screenshot of expected output](img/TEST_EimBoundingBoxes.png)

## How to train a model on Edge Impulse

todo
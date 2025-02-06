import RPi.GPIO as io

class RaspberryPiZero2:
    servoXPin = 17
    servoYPin = 18
    def __init__(self):
        # This changes the GPIO pins' specification mode to Broadcom SOC channel number (BCM). 
        # This implies that instead of specifying the physical pin numbers, you'll use the GPIO numbers for the pins you want to control
        io.setmode(io.BCM)
        io.setup(servoXPin, io.OUT)
	io.setup(servoYPin, io.OUT)


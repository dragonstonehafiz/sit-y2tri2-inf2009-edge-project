from helper.PiCameraInterface import PiCameraInterface
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.RefreshRateLimiter import FPSLimiter
from helper.MQTT import MQTT_Publisher

from enum import Enum

class STATES(Enum):
    IDLE = 0
    SCAN = 1
    TRACKING = 2
    QUIT = 3

def idle(picam: PiCameraInterface, pizero: RaspberryPiZero2, currState: list[int]):
    print("Currently in IDLE state.")
    pass

def scan(picam: PiCameraInterface, pizero: RaspberryPiZero2, state: list):
    print("Currently in SCAN state.")
    state[0] = STATES.TRACKING  # Move to tracking

def tracking(picam: PiCameraInterface, pizero: RaspberryPiZero2, state: list):
    print("Currently in TRACKING state.")
    state[0] = STATES.QUIT  # Move to quit for demonstration

if __name__ == "__main__":
    picam = PiCameraInterface((256, 256))
    pizero = RaspberryPiZero2()
    rrl = FPSLimiter(12)

    # Set up MQTT so image can be sent to desktop
    MQTT_BROKER = "192.168.29.99"
    MQTT_TOPIC = "pizero/image"
    image_publisher = MQTT_Publisher(MQTT_BROKER, MQTT_TOPIC)

    # Using a list here so that it can be passed into functions
    currState = [STATES.IDLE]
    running = True
    picam.start()

    while running:
        rrl.startFrame()

        if currState[0] == STATES.IDLE:
            idle(picam, pizero, currState)
        
        elif currState[0] == STATES.SCAN:
            scan(picam, pizero, currState)

        elif currState[0] == STATES.TRACKING:
            tracking(picam, pizero, currState)

        elif currState[0] == STATES.QUIT:
            running = False
            break

        rrl.endFrame()()

    picam.close()
    pizero.cleanup()
    

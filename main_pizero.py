from helper.PiCameraInterface import PiCameraInterface
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.FPSLimiter import FPSLimiter
from helper.MQTT import MQTT_Publisher, MQTT_IPADDR, MQTT_TOPIC_CAM
from helper.utils import convert_frame_to_bytes
from helper.mainlogic import scan_handle_x

from enum import Enum
import time

class STATES(Enum):
    IDLE = 0
    SCAN = 1
    TRACKING = 2
    QUIT = 3

def change_state(currState: list[int], nextState: int, pizero: RaspberryPiZero2):
    currState[0] = nextState
    if nextState == STATES.IDLE:
        pass
    elif nextState == STATES.SCAN:
        pizero.set_servo_x(90)
        pizero.set_servo_y(90)
        pass
    elif nextState == STATES.TRACKING:
        pass
    elif nextState == STATES.QUIT:
        pass

def idle(picam: PiCameraInterface, pizero: RaspberryPiZero2, currState: list[int]):
    """Listens for birds. If bird detected, switch to scan state"""
    time.sleep(5)
    change_state(currState, STATES.SCAN, pizero)

def scan(picam: PiCameraInterface, pizero: RaspberryPiZero2, 
         state: list[int], scanDir: list[bool, bool], 
         mqtt_client_cam: MQTT_Publisher = None):
    """Constantly rotates in the x axis"""
    frame = picam.getFrame()
    # Send image to server
    if mqtt_client_cam is not None:
        frame_bytes = convert_frame_to_bytes(frame)
        mqtt_client_cam.send(frame_bytes)

    # Turn x servo
    scan_handle_x(pizero, scanDir)

    # detect object
    # object_detected = obj_det_func
    # if object_detected:
    #     change_state(currState, STATES.TRACKING, pizero)


def tracking(picam: PiCameraInterface, pizero: RaspberryPiZero2, state: list[int]):
    print("Currently in TRACKING state.")
    state[0] = STATES.QUIT  # Move to quit for demonstration

if __name__ == "__main__":

    # To see image output
    SEND_FOOTAGE = True
    if SEND_FOOTAGE:
        mqtt_cam = MQTT_Publisher(MQTT_IPADDR, MQTT_TOPIC_CAM)
        mqtt_cam.loop_start()
    else: 
        mqtt_cam = None

    # Using a list here so that it can be passed into functions
    currState = [STATES.IDLE]

    pizero = RaspberryPiZero2()
    rrl = FPSLimiter(12)
    picam = PiCameraInterface((256, 256))
    picam.start()
    # True = turn in positive
    # 0 = x, 1 = y
    scanDir = [True, True]

    startTime = time.time()

    while True:
        rrl.startFrame()
        currentTime = time.time()

        if currState[0] == STATES.IDLE:
            idle(picam, pizero, currState)
        elif currState[0] == STATES.SCAN:
            scan(picam, pizero, currState, scanDir, mqtt_cam)
        elif currState[0] == STATES.TRACKING:
            tracking(picam, pizero, currState)
        elif currState[0] == STATES.QUIT:
            break

        if currentTime - startTime >= 30:
            break

        rrl.endFrame()

    if SEND_FOOTAGE:
        mqtt_cam.loop_stop()

    picam.close()
    pizero.cleanup()
    

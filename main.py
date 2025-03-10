from helper.PiCameraInterface import PiCameraInterface
from helper.FPSLimiter import FPSLimiter
from helper.MQTT import MQTT_Subscriber, MQTT_Publisher, MQTT_IPADDR, MQTT_TOPIC_CAM, MQTT_TOPIC_CONTROLS
from helper.utils import convert_frame_to_bytes
from helper.BoardInterface import BoardInterface
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.Arduino import Arduino
from main_logic import scan_handle_x

from enum import Enum
import time

global_data = {
    "is_running": True,
    "is_arduino": False,
    "board": None,
    "picam": None,
    "mqtt_cam": None,
    "mqtt_controls": None,
    "state": int,
    "scan_dir_x": False,
    "scan_dir_y": False
}

def server_data_callback(client, userdata, msg):
    pass

class STATES(Enum):
    IDLE = 0
    SCAN = 1
    TRACKING = 2
    QUIT = 3

def change_state(nextState: int):
    global_data['state'] = nextState

    if nextState == STATES.IDLE:
        pass
    
    elif nextState == STATES.SCAN:
        board: BoardInterface = global_data["board"]
        board.set_servo_x(90)
        board.set_servo_y(90)

    elif nextState == STATES.TRACKING:
        pass

    elif nextState == STATES.QUIT:
        pass

def idle():
    """Listens for birds. If bird detected, switch to scan state"""
    time.sleep(5)
    change_state(STATES.SCAN)

def scan():
    """Constantly rotates in the x axis"""
    picam: PiCameraInterface = global_data["picam"]
    frame = picam.getFrame()

    # Send image to server
    mqtt_cam: MQTT_Publisher = global_data["mqtt_cam"]
    if mqtt_cam is not None:
        frame_bytes = convert_frame_to_bytes(frame)
        mqtt_cam.send(frame_bytes)

    # Turn x servo, y will be handled in scan_handle_x function
    board = global_data["board"]
    scan_handle_x(board, global_data)

    # Check if we are relying on cloud for object detection
    mqtt_controls: MQTT_Subscriber = global_data["mqtt_controls"]
    if mqtt_controls is None:
        # detect object
        # object_detected = obj_det_func
        # if object_detected:
        #     change_state(currState, STATES.TRACKING, pizero)
        pass

def tracking():
    print("Currently in TRACKING state.")
    change_state(STATES.QUIT)

if __name__ == "__main__":
    # global_data["board"] = RaspberryPiZero2()
    global_data["board"] = Arduino("/dev/ttyACM0")

    # To see image output
    # comment out these lines if not using
    global_data["mqtt_cam"] = MQTT_Publisher(MQTT_IPADDR, MQTT_TOPIC_CAM)
    global_data["mqtt_cam"].loop_start()

    # Rely on server for object detection
    # comment out these lines if not using
    global_data["mqtt_controls"] = MQTT_Subscriber(MQTT_IPADDR, MQTT_TOPIC_CONTROLS, server_data_callback)
    global_data["mqtt_controls"].loop_start()

    rrl = FPSLimiter(12)
    global_data["picam"] = PiCameraInterface((640, 640))
    global_data["picam"].start()

    startTime = time.time()

    while True:
        rrl.startFrame()
        currentTime = time.time()
        currState: int = global_data["state"]

        if currState == STATES.IDLE:
            idle()
        elif currState == STATES.SCAN:
            scan()
        elif currState == STATES.TRACKING:
            tracking()
        elif currState == STATES.QUIT:
            break
        if currentTime - startTime >= 99:
            break

        rrl.endFrame()

    global_data["board"].close()
    
    if global_data["mqtt_cam"] is not None:
        global_data["mqtt_cam"].loop_stop()
    if global_data["mqtt_controls"] is not None:
        global_data["mqtt_controls"].loop_stop()
    
    

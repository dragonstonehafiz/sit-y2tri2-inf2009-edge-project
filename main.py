from helper.PiCameraInterface import PiCameraInterface
from helper.FPSLimiter import FPSLimiter
from helper.MQTT import MQTT_Subscriber, MQTT_Publisher, MQTT_IPADDR, MQTT_TOPIC_CAM, MQTT_TOPIC_PI_ZERO_CONTROLS, MQTT_TOPIC_SERVER_CONTROLS
from helper.utils import convert_frame_to_bytes
from helper.BoardInterface import BoardInterface
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.Arduino import Arduino
from main_logic import scan_handle_x

from enum import Enum
import time

global_data = {
    # App
    "is_running": True,
    "board": None,
    "picam": None,

    # Logic
    "state": int,
    "scan_dir_x": False,
    "scan_dir_y": False,
    "last_bird_time": time.time(),

    # Server
    "mqtt_cam_feed": None,
    "mqtt_cam_controls": None,
    "mqtt_server_controls": None
}

def cam_controls_callback(client, userdata, msg):
    recieved: str = msg.payload.decode()
    # Only valid messages should be recieved, so no need to make checks
    recieved = recieved.split(":")
    try:
        # Manually Change State
        if recieved[0] == "state":
            if recieved[1] == "idle":
                change_state(STATES.IDLE)
            elif recieved[1] == "scan":
                change_state(STATES.SCAN)
            elif recieved[1] == "tracking":
                change_state(STATES.TRACKING)
            elif recieved[1] == "quit":
                change_state(STATES.QUIT)
        
        # Only turn if current state is tracking
        if global_data["state"] == STATES.TRACKING:
            global_data["last_bird_time"] = time.time()

            board: BoardInterface = global_data["board"]
            if recieved[0] == "turnx":
                angle = int(recieved[1])
                board.turn_servo_x(angle)

            elif recieved[0] == "turny":
                angle = int(recieved[1])
                board.turn_servo_y(angle)

        # If the state is scanning, then any turn command means an object was detected by the server
        elif global_data["state"] == STATES.SCAN:
            if recieved[0] in ["turnx", "turny"]:
                change_state(STATES.TRACKING)

    except Exception as e:
        print(f"Exception {e}")

class STATES(Enum):
    IDLE = 0
    SCAN = 1
    TRACKING = 2
    QUIT = 3

def change_state(nextState: int):
    global_data['state'] = nextState
    board: BoardInterface = global_data["board"]

    if nextState == STATES.IDLE:
        print("Entering State Idle")

        # If relying on cloud for computation, tell server to stop detecting objects
        mqtt_server_controls: MQTT_Publisher = global_data["mqtt_server_controls"]
        if mqtt_server_controls is not None:
            mqtt_server_controls.send("auto:0")
    
    elif nextState == STATES.SCAN:
        print("Entering State Scan")
        board.set_servo_x(90)
        board.set_servo_y(90)
        board.set_laser(0)

        global_data["scan_dir_x"] = True
        global_data["scan_dir_y"] = False

        # Only do this part if relying on server for computation
        mqtt_server_controls: MQTT_Publisher = global_data["mqtt_server_controls"]
        if mqtt_server_controls is not None:
            mqtt_server_controls.send("auto:1")


    elif nextState == STATES.TRACKING:
        print("Entering State Tracking")
        board.set_laser(1)
        global_data["last_bird_time"] = time.time()

    elif nextState == STATES.QUIT:
        print("Entering State Quit")
        board.set_laser(0)

def idle():
    """Listens for birds. If bird detected, switch to scan state"""
    time.sleep(1)
    change_state(STATES.SCAN)

def scan():
    """Constantly rotates in the x axis"""
    picam: PiCameraInterface = global_data["picam"]
    frame = picam.getFrame()

    # Send image to server
    mqtt_cam_feed: MQTT_Publisher = global_data["mqtt_cam_feed"]
    if mqtt_cam_feed is not None:
        frame_bytes = convert_frame_to_bytes(frame)
        mqtt_cam_feed.send(frame_bytes)

    # Turn x servo, y will be handled in scan_handle_x function
    board = global_data["board"]
    scan_handle_x(board, global_data)

    # Check if we are relying on cloud for object detection
    mqtt_cam_controls: MQTT_Subscriber = global_data["mqtt_cam_controls"]
    if mqtt_cam_controls is None:
        # detect object
        # object_detected = obj_det_func
        # if object_detected:
        #     change_state(currState, STATES.TRACKING, pizero)
        pass

def tracking():
    picam: PiCameraInterface = global_data["picam"]
    frame = picam.getFrame()

    # Send image to server
    mqtt_cam_feed: MQTT_Publisher = global_data["mqtt_cam_feed"]
    if mqtt_cam_feed is not None:
        frame_bytes = convert_frame_to_bytes(frame)
        mqtt_cam_feed.send(frame_bytes)

    # Go back to idle state if no bird is detected for a period of time
    last_bird_time = global_data["last_bird_time"]
    current_time = time.time()
    if current_time - last_bird_time > 15:
        change_state(STATES.IDLE)

if __name__ == "__main__":
    # global_data["board"] = RaspberryPiZero2()
    global_data["board"] = Arduino("/dev/ttyACM0")

    SEND_IMAGE_DATA = True
    if SEND_IMAGE_DATA:
        # To see image output
        global_data["mqtt_cam_feed"] = MQTT_Publisher(MQTT_IPADDR, MQTT_TOPIC_CAM)
        global_data["mqtt_cam_feed"].loop_start()

    SERVER_PROCESSING = True
    if SERVER_PROCESSING:
        # To tell server to start looking at images
        global_data["mqtt_server_controls"] = MQTT_Publisher(MQTT_IPADDR, MQTT_TOPIC_SERVER_CONTROLS)
        global_data["mqtt_server_controls"].loop_start()

        # Rely on server for object detection
        global_data["mqtt_cam_controls"] = MQTT_Subscriber(MQTT_IPADDR, MQTT_TOPIC_PI_ZERO_CONTROLS, cam_controls_callback)
        global_data["mqtt_cam_controls"].loop_start()

    rrl = FPSLimiter(12)
    global_data["picam"] = PiCameraInterface((640, 640))
    global_data["picam"].start()

    startTime = time.time()
    global_data["state"] = STATES.IDLE

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
        if currentTime - startTime >= 30:
            break

        rrl.endFrame()

    global_data["board"].close()
    
    if global_data["mqtt_cam_feed"] is not None:
        global_data["mqtt_cam_feed"].loop_stop()
    if global_data["mqtt_cam_controls"] is not None:
        global_data["mqtt_cam_controls"].loop_stop()
    if global_data["mqtt_server_controls"] is not None:
        global_data["mqtt_server_controls"].loop_stop()
    
    
    

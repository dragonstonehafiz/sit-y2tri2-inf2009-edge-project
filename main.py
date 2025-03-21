from helper.PiCameraInterface import PiCameraInterface
from helper.FPSLimiter import FPSLimiter
from helper.MQTT import MQTT_Subscriber, MQTT_Publisher, MQTT_TOPIC_CAM, MQTT_TOPIC_PI_ZERO_CONTROLS, MQTT_TOPIC_SERVER_CONTROLS
from helper.utils import convert_frame_to_bytes, get_closest_coords, get_object_displacement
from helper.BoardInterface import BoardInterface
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.YoloV5_ONNX import YoloV5_ONNX, YOLOv5
from helper.AudioInterface import AudioInterface
from main_helper import scan_handle_x, record_audio_thread, STATES

import time
import traceback
import threading
import sys

global_data = {
    # App
    "is_running": True,
    "board": None,
    "yolov5": None,

    # Cam
    "picam": None,
    "cam_resolution": 192,
    "cam_size": (192, 192),
    "cam_center": (96, 96),

    # Logic
    "state": int,
    "scan_dir_x": False,
    "scan_dir_y": False,
    "last_bird_time": time.time(),
    "most_recent_sound": None,
    "most_recent_sound_peak_amp": None, 

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

def init():
    global_data["board"] = RaspberryPiZero2()
    # global_data["board"] = Arduino("/dev/ttyACM0")

    SEND_IMAGE_DATA = True
    SERVER_PROCESSING = False
    MQTT_IPADDR = input("Input Server IP Address: ")
    CAM_RESOLUTION = global_data["cam_resolution"]

    # Load MQTT Connection
    try:
        if SEND_IMAGE_DATA:
            # To see image output
            global_data["mqtt_cam_feed"] = MQTT_Publisher(MQTT_IPADDR, MQTT_TOPIC_CAM)
            global_data["mqtt_cam_feed"].loop_start()

        if SERVER_PROCESSING:
            # To tell server to start looking at images
            global_data["mqtt_server_controls"] = MQTT_Publisher(MQTT_IPADDR, MQTT_TOPIC_SERVER_CONTROLS)
            global_data["mqtt_server_controls"].loop_start()

            # Rely on server for object detection
            global_data["mqtt_cam_controls"] = MQTT_Subscriber(MQTT_IPADDR, MQTT_TOPIC_PI_ZERO_CONTROLS, cam_controls_callback)
            global_data["mqtt_cam_controls"].loop_start()
        else:
            global_data["yolov5"] = YoloV5_ONNX(f"model/yolov5n_{CAM_RESOLUTION}.onnx", image_size=(CAM_RESOLUTION, CAM_RESOLUTION))
            pass
    except Exception as e:
        print(f"Failed to connect to MQTT Broker: {e}")
        traceback.print_exc()
        print("\nQuitting\n")
        sys.exit()

    # Picam
    try:
        global_data["picam"] = PiCameraInterface((CAM_RESOLUTION, CAM_RESOLUTION))
        global_data["picam"].start()
    except Exception as e:
        print(f"Error starting PiCamera: {e}")
        traceback.print_exc()
        print("\nQuitting\n")
        sys.exit()

def change_state(nextState: int):
    global_data['state'] = nextState
    board: BoardInterface = global_data["board"]

    if nextState == STATES.IDLE:
        print("Entering State Idle")
        board.set_laser(0)

        # If relying on cloud for computation, tell server to stop detecting objects
        mqtt_server_controls: MQTT_Publisher = global_data["mqtt_server_controls"]
        if mqtt_server_controls is not None:
            mqtt_server_controls.send("auto:0")
    
    elif nextState == STATES.SCAN:
        print("Entering State Scan")
        board.set_laser(0)

        global_data["scan_dir_x"] = True
        global_data["scan_dir_y"] = False

        # If relying on cloud, tell server to start sending turn orders based on model detected
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
        global_data["is_running"] = False

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
    scan_handle_x(board, global_data, servo_turn_rate_x=2)

    # Check if we are relying on cloud for object detection
    mqtt_cam_controls: MQTT_Subscriber = global_data["mqtt_cam_controls"]
    if mqtt_cam_controls is None:
        yolov5: YOLOv5 = global_data["yolov5"]

        try:
            detections = yolov5.detect_objects(frame, conf_thres=0.5)
            # If object is found, change state to tracking
            if len(detections) > 0:
                change_state(STATES.TRACKING)
        except Exception as e:
            print(f"Error {e}")
            traceback.print_exc()
            change_state(STATES.QUIT)

def tracking():
    picam: PiCameraInterface = global_data["picam"]
    frame = picam.getFrame()

    # Send image to server
    mqtt_cam_feed: MQTT_Publisher = global_data["mqtt_cam_feed"]
    if mqtt_cam_feed is not None:
        frame_bytes = convert_frame_to_bytes(frame)
        mqtt_cam_feed.send(frame_bytes)

    # If we are not relying on server for processing, do it here
    mqtt_cam_controls: MQTT_Subscriber = global_data["mqtt_cam_controls"]
    if mqtt_cam_controls is None:
        board: BoardInterface = global_data["board"]
        yolov5: YOLOv5 = global_data["yolov5"]
        try:
            detections = yolov5.detect_objects(frame, conf_thres=0.5)

            # If objects were found, find the coords of the closest one
            if len(detections) > 0:
                obj_center = get_closest_coords(global_data["cam_center"], detections)

                # calculate displacement of obj from center
                # then normalize it so it is not some crazy large number
                dispX, dispY = get_object_displacement(obj_center, global_data["cam_center"], global_data["cam_size"])
                if abs(dispX) > 1:
                    board.turn_servo_x(dispX)
                if abs(dispY) > 1:
                    board.turn_servo_y(dispY)
                
                global_data["last_bird_time"] = time.time()
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            change_state(STATES.QUIT)


    # Go back to idle state if no bird is detected for a period of time
    last_bird_time = global_data["last_bird_time"]
    current_time = time.time()
    if current_time - last_bird_time > 15:
        change_state(STATES.IDLE)

if __name__ == "__main__":
    init()

    # FPSLimiter controls the number of 5
    rrl = FPSLimiter(6)

    # This is just to force quit the system after a certain time
    startTime = time.time()
    change_state(STATES.IDLE)

    # Start thread for recording audio
    # audio_thread = threading.Thread(target=lambda x: {record_audio_thread(global_data)}, daemon=True)
    # audio_thread.start()

    while global_data["is_running"]:
        rrl.startFrame()
        currentTime = time.time()
        currState: int = global_data["state"]

        try:
            if currState == STATES.IDLE:
                idle()
            elif currState == STATES.SCAN:
                scan()
            elif currState == STATES.TRACKING:
                tracking()
            elif currState == STATES.QUIT:
                break
            if currentTime - startTime >= 999:
                global_data["is_running"] = False
                break
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            change_state(STATES.QUIT)
        except KeyboardInterrupt as e:
            print(f"Error: {e}")
            change_state(STATES.QUIT)
        
        rrl.endFrame()
        print(f"Frame Rate: {1 / rrl.getDeltaTime():0.2f}")

    global_data["board"].close()
    
    if global_data["mqtt_cam_feed"] is not None:
        global_data["mqtt_cam_feed"].loop_stop()
    if global_data["mqtt_cam_controls"] is not None:
        global_data["mqtt_cam_controls"].loop_stop()
    if global_data["mqtt_server_controls"] is not None:
        global_data["mqtt_server_controls"].loop_stop()
    
    
    

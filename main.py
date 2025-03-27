from helper.PiCameraInterface import PiCameraInterface
from helper.FPSLimiter import FPSLimiter
from helper.MQTT import MQTT_Subscriber, MQTT_Publisher, MQTT_TOPIC_CAM, MQTT_TOPIC_PI_ZERO_CONTROLS, MQTT_TOPIC_SERVER_CONTROLS
from helper.utils import get_closest_coords, get_object_displacement
from helper.BoardInterface import BoardInterface
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.YoloV5_ONNX import YoloV5_ONNX, YOLOv5
from helper.sound import load_model, capture_and_predict
from main_helper import scan_handle_x, STATES, handle_picam

import time
import traceback
import threading
import sys
import os
import argparse

global_data = {
    # App
    "is_running": True,
    "board": None,
    "yolov5": None,

    # Cam
    "picam": None,
    "cam_resolution": 256,
    "cam_size": (256, 256),
    "cam_center": (256/2, 256/2),
    "curr_frame": None,

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

def thread_model():
    os.sched_setaffinity(0, {1, 2, 3})
    CAM_RESOLUTION = global_data["cam_resolution"]
    yolov5 = YoloV5_ONNX(f"model/yolov5n_{CAM_RESOLUTION}.onnx", image_size=(CAM_RESOLUTION, CAM_RESOLUTION))
    mqtt_cam_controls: MQTT_Subscriber = global_data["mqtt_cam_controls"]
    rrl = FPSLimiter(3)
    session = load_model()
    time.sleep(1)

    while global_data["is_running"]:
        try:
            rrl.startFrame()
            frame = global_data["curr_frame"].copy()

            if global_data["state"] == STATES.IDLE:
                capture_and_predict(session)

            elif global_data["state"] == STATES.SCAN:
                # Check if we are relying on cloud for object detection
                if mqtt_cam_controls is None:
                    try:
                        detections = yolov5.detect_objects(frame, conf_thres=0.4)
                        # If object is found, change state to tracking
                        if len(detections) > 0:
                            change_state(STATES.TRACKING)
                    except Exception as e:
                        print(f"Error {e}")
                        traceback.print_exc()
                        change_state(STATES.QUIT)
            
            elif global_data["state"] == STATES.TRACKING:
                # If we are not relying on server for processing, do it here
                if mqtt_cam_controls is None:
                    board: BoardInterface = global_data["board"]
                    try:
                        detections = yolov5.detect_objects(frame, conf_thres=0.5)

                        # If objects were found, find the coords of the closest one
                        if len(detections) > 0:
                            obj_center = get_closest_coords(global_data["cam_center"], detections)

                            # calculate displacement of obj from center
                            # then normalize it so it is not some crazy large number
                            dispX, dispY = get_object_displacement(obj_center, global_data["cam_center"], global_data["cam_size"])
                            if abs(dispX) > 1:
                                threading.Thread(target=board.turn_servo_x, args=(dispX,)).start()
                            if abs(dispY) > 1:
                                threading.Thread(target=board.turn_servo_y, args=(dispY,)).start()
                            
                            global_data["last_bird_time"] = time.time()
                    except Exception as e:
                        traceback.print_exc()
                        print(f"Error: {e}")
                        change_state(STATES.QUIT)
                        pass
            
            elif global_data["state"] == STATES.QUIT:
                break

            rrl.endFrame()
            # print(f"Frame Rate: {1 / rrl.getDeltaTime():0.2f}")
            # print(f"Delta Time: {rrl.getDeltaTime():0.2f}")
        except Exception as e:
            traceback.print_stack()
            print(f"Error: {e}")

def init(server_processing=False, cam_resolution=256, send_image_data=True):
    SEND_IMAGE_DATA = send_image_data
    SERVER_PROCESSING = server_processing

    if SEND_IMAGE_DATA or SERVER_PROCESSING:
        MQTT_IPADDR = input("Input Server IP Address: ")
    else:
        print("Server not being used.")

    # Set camera size
    if cam_resolution not in [128, 160, 192, 224, 256]:
        print("Camera resolution not supported. Defaulting to 192.")
        cam_resolution = 224
    CAM_RESOLUTION = cam_resolution
    global_data["cam_resolution"] = CAM_RESOLUTION
    global_data["cam_size"] = (CAM_RESOLUTION, CAM_RESOLUTION)
    global_data["cam_center"] = (CAM_RESOLUTION / 2, CAM_RESOLUTION / 2)

    # Load MQTT Connection
    try:
        if SEND_IMAGE_DATA or SERVER_PROCESSING:
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
            threading.Thread(target=thread_model, daemon=True).start()
    except Exception as e:
        print(f"Failed to connect to MQTT Broker: {e}")
        traceback.print_exc()
        print("\nQuitting\n")
        sys.exit()

    # Load Board
    try:
        global_data["board"] = RaspberryPiZero2()
        # global_data["board"] = Arduino("/dev/ttyACM0")
    except Exception as e:
        traceback.print_exc()
        print(f"Error when loading board: {e}")
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
    # Turn x servo, y will be handled in scan_handle_x function
    scan_handle_x(global_data["board"], global_data, servo_turn_rate_x=2)

def tracking():
    # Go back to idle state if no bird is detected for a period of time
    last_bird_time = global_data["last_bird_time"]
    current_time = time.time()
    if current_time - last_bird_time > 15:
        change_state(STATES.IDLE)

if __name__ == "__main__":
    # Check for CLI arguments
    parser = argparse.ArgumentParser(description="Run object detection with local or server processing.")
    parser.add_argument("--server", choices=["true", "false"], required=True,
                        help="Whether to use server-side object detection (true/false)")
    parser.add_argument("--cam-size", type=int, required=True,
                        help="Camera resolution (128, 160, 192, 224, 256)")
    parser.add_argument("--send-image", choices=["true", "false"], required=True,
                        help="Whether to send image data to the server via MQTT (true/false)")
    args = parser.parse_args()

    # Convert string inputs to booleans
    use_server = args.server.lower() == "true"
    send_image = args.send_image.lower() == "true"
    init(server_processing=args.server, cam_resolution=use_server, send_image_data=send_image)

    # FPSLimiter controls the number of 5
    rrl = FPSLimiter(6)

    # Initialize State Machine
    change_state(STATES.IDLE)

    # Main Loop
    while global_data["is_running"]:
        try:
            rrl.startFrame()
            currState: int = global_data["state"]

            # Get the picam view for this frame
            handle_picam(global_data)

            if currState == STATES.IDLE:
                idle()
            elif currState == STATES.SCAN:
                scan()
            elif currState == STATES.TRACKING:
                tracking()
            elif currState == STATES.QUIT:
                global_data["is_running"] = False
                break

            rrl.endFrame()
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            change_state(STATES.QUIT)
        except KeyboardInterrupt as e:
            print(f"Error: {e}")
            change_state(STATES.QUIT)
        
        # print(f"Frame Rate: {1 / rrl.getDeltaTime():0.2f}")

    global_data["board"].close()
    
    if global_data["mqtt_cam_feed"] is not None:
        global_data["mqtt_cam_feed"].loop_stop()
    if global_data["mqtt_cam_controls"] is not None:
        global_data["mqtt_cam_controls"].loop_stop()
    if global_data["mqtt_server_controls"] is not None:
        global_data["mqtt_server_controls"].loop_stop()
    
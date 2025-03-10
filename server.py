from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.MQTT import MQTT_TOPIC_CAM, MQTT_TOPIC_PI_ZERO_CONTROLS, MQTT_TOPIC_SERVER_CONTROLS
from helper.YoloV5 import YOLOv5
from helper.utils import convert_bytes_to_frame, get_closest_coords, get_object_displacement

import time
import cv2
import queue
import numpy as np
import threading

global_data = {
    "is_running": True,
    # Rendering
    "frame_queue": queue.Queue(),
    "last_frame_time": time.time(),

    # Camera
    "cam_size": (640, 640),
    "cam_center": (320, 320),

    # Servers
    "mqtt_server_controls": None,
    "mqtt_cam_controls": None,
    "mqtt_cam_feed": None,

    # Object Detection
    "auto": False,
    "yolov5": YOLOv5("yolov5s")
    }

def camera_data_callback(client, userdata, msg):
    frame = convert_bytes_to_frame(msg.payload)
    global_data["frame_queue"].put(frame)
    global_data["last_frame_time"] = time.time()

    if global_data["auto"]:
        yolov5: YOLOv5 = global_data["yolov5"]
        detections = yolov5.detect_objects(lastimage) 

        # If objects were found, find the coords of the closest one
        if len(detections) > 0:
            obj_center = get_closest_coords(global_data["cam_center"], detections)

            # calculate displacement of obj from center
            # then normalize it so it is not some crazy large number
            dispX, dispY = get_object_displacement(obj_center, global_data["cam_center"], global_data["cam_size"])
            if abs(dispX) > 1:
                mqtt_cam_controls.send(f"turnx:{dispX}")
            if abs(dispY):
                mqtt_cam_controls.send(f"turny:{dispY}")

def server_commands_callback(client, userdata, msg):
    message = msg.payload.decode()

    print(message)
    # Only valid messages should be recieved, so no need to make checks
    recieved = message.split(":")
    if recieved[0] == "auto":
        global_data["auto"] = int(recieved[1])

def get_user_input():
    commands_help = """
    Commands

    turnx:<angle>
    turny:<angle>
    setx:<angle>
    sety:<angle>

    quit:both
    quit:cam
    quit:server

    auto:1
    auto:0

    laser:1
    laser:0
    """

    # delay so that the first input message doesn't appear before connecting to server
    time.sleep(1.5)
    mqtt_cam_controls: MQTT_Subscriber = global_data["mqtt_cam_controls"]
    while True:
        action = input("Enter Command: ")
        action = action.lower()
        # check if command is valid
        if ":" in action:
            parts = action.split(':')
            # only accept inputs with two parts
            if len(parts) != 2:
                print("Invalid Input")
                
            # validates commands
            else:
                # If action is turning/setting angle and second part is not number
                # then it is an invalid command
                if parts[0] in ["turnx", "turny", "setx", "sety"]:
                    try:
                        value = float(parts[1])
                    except ValueError:
                        print(commands_help)
                        continue    
                    mqtt_cam_controls.send(action)

                # If action is laser, and it is not '1' or '0'
                elif parts[0] == "laser" and parts[1] in ['1', '0']:
                    mqtt_cam_controls.send(action)

                # setting auto mode
                elif parts[0] == "auto" and parts[1] in ['1', '0']:
                    if parts[1] == "1":
                        global_data["auto"] = True
                    elif parts[1] == "1":
                        global_data["auto"] = False
                    else:
                        print(commands_help)

                # quitting program
                elif parts[0] == "quit":
                    # quit for both cam and server
                    if parts[1] == "both":
                        mqtt_cam_controls.send(f"{action}:x")
                        global_data["is_running"] = False
                        break
                    elif parts[1] == "server":
                        global_data["is_running"] = False
                        break
                    elif parts[1] == "cam":
                        mqtt_cam_controls.send(f"{action}:x")
                    else:
                        print(commands_help)
                
                # error
                else:
                    print(commands_help)

        else:
            print(commands_help)
                    

if __name__ == "__main__":
    print("Starting Server")
    mqtt_cam_controls = MQTT_Publisher("localhost", MQTT_TOPIC_PI_ZERO_CONTROLS)
    mqtt_cam_feed = MQTT_Subscriber('localhost', MQTT_TOPIC_CAM, camera_data_callback)
    mqtt_server_controls = MQTT_Subscriber('localhost', MQTT_TOPIC_SERVER_CONTROLS, server_commands_callback)
    time.sleep(1)

    # Start controls thread
    thread = threading.Thread(target=get_user_input, daemon=False)
    thread.start()

    global_data["mqtt_cam_controls"] = mqtt_cam_controls
    global_data["mqtt_cam_feed"] = mqtt_cam_feed
    global_data["mqtt_server_controls"] = mqtt_server_controls

    # Start network loops
    mqtt_cam_feed.loop_start()
    mqtt_cam_controls.loop_start()
    mqtt_server_controls.loop_start()

    while True:
        current_time = time.time()
        frame_queue: queue.Queue = global_data["frame_queue"]
        if not frame_queue.empty():
            lastimage = frame_queue.get()
                    
        elif current_time - global_data["last_frame_time"] > 1:
            lastimage = np.zeros((640, 640, 3), dtype=np.uint8)

        cv2.imshow("Received Image", lastimage)

        if (cv2.waitKey(1) & 0xFF == ord('q')) or global_data["is_running"] == False:
            break
    
    cv2.destroyAllWindows()

    mqtt_cam_feed.loop_stop()
    mqtt_cam_feed.disconnect()
    mqtt_cam_controls.loop_stop()
    mqtt_cam_controls.disconnect()
    mqtt_server_controls.loop_stop()
    mqtt_server_controls.disconnect()

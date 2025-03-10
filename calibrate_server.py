from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.MQTT import MQTT_TOPIC_CAM, MQTT_TOPIC_CONTROLS
from helper.YoloV5 import YOLOv5
from helper.utils import convert_bytes_to_frame, get_closest_coords, get_object_displacement

import time
import cv2
import queue
import numpy as np
import threading

global_data = {
    "frame_queue": queue.Queue(),
    "last_frame_time": time.time(),
    "is_running": True,
    "auto": False,
    "cam_size": (640, 640),
    "cam_center": (320, 320)
    }

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

def camera_data_callback(client, userdata, msg):
    frame = convert_bytes_to_frame(msg.payload)
    global_data["frame_queue"].put(frame)
    global_data["last_frame_time"] = time.time()


def get_user_input(mqtt_controls: MQTT_Publisher):
    # delay so that the first input message doesn't appear before connecting to server
    time.sleep(1.5)
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
                    mqtt_controls.send(action)

                # If action is laser, and it is not '1' or '0'
                elif parts[0] == "laser" and parts[1] in ['1', '0']:
                    mqtt_controls.send(action)

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
                        mqtt_controls.send(f"{action}:x")
                        global_data["is_running"] = False
                        break
                    elif parts[1] == "server":
                        global_data["is_running"] = False
                        break
                    elif parts[1] == "cam":
                        mqtt_controls.send(f"{action}:x")
                    else:
                        print(commands_help)
                
                # error
                else:
                    print(commands_help)

        else:
            print(commands_help)
                    
    

if __name__ == "__main__":
    print("Starting Server")
    mqtt_controls = MQTT_Publisher("localhost", MQTT_TOPIC_CONTROLS)
    mqtt_cam = MQTT_Subscriber('localhost', MQTT_TOPIC_CAM, camera_data_callback)
    time.sleep(1)

    # Start controls thread
    thread = threading.Thread(target=lambda: {get_user_input(mqtt_controls)}, daemon=False)
    thread.start()

    # Start network loops
    mqtt_cam.loop_start()
    mqtt_controls.loop_start()

    # Load YoloV5 model
    yolov5 = YOLOv5("yolov5s")

    while True:
        current_time = time.time()
        frame_queue: queue.Queue = global_data["frame_queue"]
        if not frame_queue.empty():
            lastimage = frame_queue.get()
            detections = yolov5.detect_objects(lastimage) 

            # If objects were found, find the coords of the closest one
            if len(detections) > 0:
                obj_center = get_closest_coords(global_data["cam_center"], detections)
                cv2.circle(lastimage, obj_center, 10, (0, 255, 0))

                if global_data["auto"]:
                    # calculate displacement of obj from center
                    # then normalize it so it is not some crazy large number
                    dispX, dispY = get_object_displacement(obj_center, global_data["cam_center"], global_data["cam_size"])
                    if abs(dispX) > 2:
                        mqtt_controls.send(f"turnx:{dispX}")
                    if abs(dispY):
                        mqtt_controls.send(f"turny:{dispY}")
                    
        elif current_time - global_data["last_frame_time"] > 1:
            lastimage = np.zeros((640, 640, 3), dtype=np.uint8)

        cv2.imshow("Received Image", lastimage)

        if (cv2.waitKey(1) & 0xFF == ord('q')) or global_data["is_running"] == False:
            break
    
    cv2.destroyAllWindows()
    mqtt_cam.loop_stop()
    mqtt_controls.loop_stop()
    mqtt_cam.disconnect()
    mqtt_controls.disconnect()

from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.MQTT import MQTT_TOPIC_CAM, MQTT_TOPIC_CONTROLS
from helper.utils import convert_bytes_to_frame

import time
import cv2
import queue
import numpy as np
import threading

frame_queue = queue.Queue()  # Queue to hold frames from MQTT
last_frame_time: list[float] = [time.time()] # Store last frame time in list so that it is mutable
is_running = [True]

def camera_data_callback(client, userdata, msg):
    frame = convert_bytes_to_frame(msg.payload)
    frame_queue.put(frame)
    cv2.imshow("Received Image", frame)
    last_frame_time[0] = time.time()


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
            # this else statement checks for invalid commands and sends messages appropriately
            else:
                # If action is turning/setting angle and second part is not number
                # then it is an invalid command
                if parts[0] in ["turnx", "turny", "setx", "sety"] and not parts[1].isnumeric():
                    print("These commands should be accompanied by numbers")
                    continue
                # If action is laser, and it is not '1' or '0'
                # then it is an invalid command
                elif parts[0] == "laser" and parts[1] not in ['1', '0']:
                    print("Laser value can only be '1' or '0'")
                    continue
                elif parts[0] not in ["turnx", "turny", "setx", "sety", "laser", "message"]:
                    print("Invalid command | Example commands\n 'turnx:180', 'quit' ")
                    continue
                mqtt_controls.send(action)
        elif action[:4] == "quit":
            # Putting the : at the end so that we can user split() in the pizero when recieving commands
            mqtt_controls.send(f"{action}:x")
            is_running[0] = False
            break
        else:
            print("Invalid command | Example commands\n 'turnx:180', 'quit' ")
                    
    

if __name__ == "__main__":
    print("Starting Server")
    mqtt_controls = MQTT_Publisher("localhost", MQTT_TOPIC_CONTROLS)
    mqtt_cam = MQTT_Subscriber('localhost', MQTT_TOPIC_CAM, camera_data_callback)
    time.sleep(1)

    # Start network loops
    mqtt_cam.loop_start()
    mqtt_controls.loop_start()

    # Start controls thread
    thread = threading.Thread(target=lambda: {get_user_input(mqtt_controls)}, daemon=True)
    thread.start()

    while True:
        current_time = time.time()
        if current_time - last_frame_time[0] > 0.5:
            # Create a black image (all zeros = black)
            black_screen = np.zeros((640, 640, 3), dtype=np.uint8)
            cv2.imshow('Received Image', black_screen)

        if (cv2.waitKey(1) & 0xFF == ord('q')) or is_running[0] == False:
            break
    
    cv2.destroyAllWindows()
    mqtt_cam.loop_stop()
    mqtt_cam.disconnect()
    mqtt_controls.loop_stop()
    mqtt_controls.disconnect()

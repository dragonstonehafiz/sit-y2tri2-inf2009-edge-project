from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.MQTT import MQTT_TOPIC_CAM, MQTT_TOPIC_CONTROLS
from helper.utils import convert_bytes_to_frame

import time
import cv2
import queue
import numpy as np

frame_queue = queue.Queue()  # Queue to hold frames from MQTT
last_frame_time: list[float] = [time.time()] # Store last frame time in list so that it is mutable

def camera_data_callback(client, userdata, msg):
    frame = convert_bytes_to_frame(msg.payload)
    frame_queue.put(frame)
    last_frame_time[0] = time.time()

if __name__ == "__main__":
    mqtt_controls = MQTT_Publisher("localhost", MQTT_TOPIC_CONTROLS)
    mqtt_cam = MQTT_Subscriber('localhost', MQTT_TOPIC_CAM, camera_data_callback)

    print("Starting Server")
    mqtt_cam.loop_start()
    time.sleep(1)

    while True:
        current_time = time.time()
        if not frame_queue.empty():
            frame = frame_queue.get()
            lastimage = frame
            cv2.imshow("Received Image", lastimage)
        elif current_time - last_frame_time[0] > 0.5:
            # Create a black image (all zeros = black)
            black_screen = np.zeros((640, 640, 3), dtype=np.uint8)

            # Display the black screen
            cv2.imshow('Received Image', black_screen)

        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
    
    cv2.destroyAllWindows()
    mqtt_cam.loop_stop()
    mqtt_cam.disconnect()
    mqtt_controls.disconnect()

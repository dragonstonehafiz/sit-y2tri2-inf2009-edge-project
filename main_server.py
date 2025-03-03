from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.utils import convert_bytes_to_frame
import cv2
import numpy as np
import queue

frame_queue = queue.Queue()  # Queue to hold frames from MQTT

def camera_data_callback(client, userdata, msg):
    frame = convert_bytes_to_frame(msg.payload)
    frame_queue.put(frame)

if __name__ == "__main__":
    # The server will be the desktop/rasberry pi
    mqtt_turn_data = MQTT_Publisher("localhost", "pizero/turn")
    mqtt_image_data = MQTT_Subscriber("localhost", "pizero/image", camera_data_callback)

    lastimage = np.zeros((480, 640, 3), dtype=np.uint8)

    mqtt_image_data.loop_start()
    while True:
        try:
            if not frame_queue.empty():
                frame = frame_queue.get()
                lastimage = frame
            cv2.imshow("Received Image", lastimage)
        except Exception as e:
            break

        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break

    cv2.destroyAllWindows()
    mqtt_image_data.loop_stop()
    mqtt_image_data.disconnect()
    mqtt_turn_data.disconnect()
     
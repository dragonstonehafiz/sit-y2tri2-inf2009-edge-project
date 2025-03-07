from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.MQTT import MQTT_TOPIC_CAM, MQTT_TOPIC_CONTROLS
from helper.utils import convert_bytes_to_frame

import cv2

def camera_data_callback(client, userdata, msg):
    frame = convert_bytes_to_frame(msg.payload)
    cv2.imshow("Received Image", frame)

if __name__ == "__main__":
    mqtt_controls = MQTT_Publisher("localhost", MQTT_TOPIC_CONTROLS)
    mqtt_cam = MQTT_Subscriber('localhost', MQTT_TOPIC_CAM, camera_data_callback)

    while True:
        action = input("What do you want to do?")
        if action == quit:
            break
    
    cv2.destroyAllWindows()

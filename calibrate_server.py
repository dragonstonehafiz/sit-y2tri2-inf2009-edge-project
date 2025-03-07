from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.MQTT import MQTT_TOPIC_CAM, MQTT_TOPIC_CONTROLS
from helper.utils import convert_bytes_to_frame

import cv2

def camera_data_callback(client, userdata, msg):
    frame = convert_bytes_to_frame(msg.payload)
    # print("here")
    cv2.imshow("Received Image", frame)

if __name__ == "__main__":
    mqtt_controls = MQTT_Publisher("localhost", MQTT_TOPIC_CONTROLS)
    mqtt_cam = MQTT_Subscriber('localhost', MQTT_TOPIC_CAM, camera_data_callback)

    print("Starting Server")
    
    mqtt_cam.loop_start()
    while True:
        action = input("Action:")
        if action == "quit":
            break
        pass
    
    cv2.destroyAllWindows()
    mqtt_cam.loop_stop()
    mqtt_cam.disconnect()
    mqtt_controls.disconnect()

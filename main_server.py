from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.utils import convert_bytes_to_frame
import cv2

def camera_data_callback(client, userdata, msg):
    frame = convert_bytes_to_frame(msg.payload)
    # Display image
    cv2.imshow("Received Image", frame)

if __name__ == "__main__":
    # The server will be the desktop/rasberry pi
    mqtt_turn_data = MQTT_Publisher("localhost", "pizero/turn")
    mqtt_image_data = MQTT_Subscriber("localhost", "pizero/image", camera_data_callback)

    while True:
        pass
     
from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.MQTT import MQTT_TOPIC_CAM, MQTT_TOPIC_CONTROLS, MQTT_IPADDR
from helper.utils import convert_frame_to_bytes
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.FPSLimiter import FPSLimiter
from helper.PiCameraInterface import PiCameraInterface

import time

pizero = RaspberryPiZero2()

def control_data_callback(client, userdata, msg):
    recieved: str = msg.payload.decode()
    print(recieved)
    # If ',' not in the message, then there is no valid command
    if ',' not in recieved:
        return
    
    # action,value
    else:
         recieved = recieved.split(",")

if __name__ == "__main__":
    picam = PiCameraInterface()
    try:
        picam.start()
    except Exception as e:
        print(f"Error {e}")
        print("Quitting")
        quit()

    # Server
    mqtt_client_cam = MQTT_Publisher(MQTT_IPADDR, MQTT_TOPIC_CAM)
    mqtt_client_controls = MQTT_Subscriber(MQTT_IPADDR, MQTT_TOPIC_CONTROLS, control_data_callback)
    mqtt_client_controls.loop_start()

    # Send camera feed 12 times a second
    fps_controller = FPSLimiter()
    startTime = time.time()

    while True:
        fps_controller.startFrame()

        frame = picam.getFrame()
        frame_bytes = convert_frame_to_bytes(frame)
        mqtt_client_cam.send(frame_bytes)

        # Force quit after 15 seconds
        currentTime = time.time()
        if currentTime - startTime > 15:
            break

        fps_controller.endFrame()

    pizero.cleanup()
    picam.close()

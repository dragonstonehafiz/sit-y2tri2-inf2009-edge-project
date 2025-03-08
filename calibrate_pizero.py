from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.MQTT import MQTT_TOPIC_CAM, MQTT_TOPIC_CONTROLS, MQTT_IPADDR
from helper.utils import convert_frame_to_bytes
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.FPSLimiter import FPSLimiter
from helper.PiCameraInterface import PiCameraInterface

import time

pizero = RaspberryPiZero2()
isRunning = [True]

def control_data_callback(client, userdata, msg):
    recieved: str = msg.payload.decode()
    print(recieved)
    # Only valid messages should be recieved, so no need to make checks
    recieved = recieved.split(":")
    if recieved[0] == "quit":
        isRunning[0] = False
    elif recieved[0] == "turnx":
        pizero.turnServoX(int(recieved[1]))
    elif recieved[0] == "turny":
        pizero.turnServoY(int(recieved[1]))
    elif recieved[0] == "setx":
        pizero.setServoX(int(recieved[1]))
    elif recieved[0] == "sety":
        pizero.setServoY(int(recieved[1]))
    elif recieved[0] == "laser":
        if pizero[1] == "1":
            pizero.setLaser(1)
        else:
            pizero.setLaser(0)
    else:
        print("Invalid Message")

            
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

        # Send camera feed to server
        frame = picam.getFrame()
        frame_bytes = convert_frame_to_bytes(frame)
        mqtt_client_cam.send(frame_bytes)

        # Force quit after 15 seconds
        currentTime = time.time()
        if currentTime - startTime > 60:
            break

        if not isRunning[0]:
            break

        fps_controller.endFrame()

    mqtt_client_cam.loop_stop()
    mqtt_client_cam.disconnect()
    mqtt_client_controls.loop_stop()
    mqtt_client_controls.disconnect()
    pizero.cleanup()
    picam.close()

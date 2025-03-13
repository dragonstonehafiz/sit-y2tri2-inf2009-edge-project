from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.MQTT import MQTT_TOPIC_CAM, MQTT_TOPIC_PI_ZERO_CONTROLS
from helper.utils import convert_frame_to_bytes
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.Arduino import Arduino
from helper.BoardInterface import BoardInterface
from helper.FPSLimiter import FPSLimiter
from helper.PiCameraInterface import PiCameraInterface

import time
import threading
import sys

global_data = {
    "is_running": True
}

# board = Arduino("/dev/ttyACM0")
board = RaspberryPiZero2()

# def servo_thread(function: callable, angle: float, core_id):


def control_data_callback(client, userdata, msg):
    recieved: str = msg.payload.decode()
    # Only valid messages should be recieved, so no need to make checks
    recieved = recieved.split(":")
    if recieved[0] == "quit":
        global_data["is_running"] = False

    elif recieved[0] == "turnx":
        angle = int(recieved[1])
        threading.Thread(target=board.turn_servo_x, args=(angle,)).start()

    elif recieved[0] == "turny":
        angle = int(recieved[1])
        threading.Thread(target=board.turn_servo_y, args=(angle,)).start()

    elif recieved[0] == "setx":
        angle = int(recieved[1])
        threading.Thread(target=board.set_servo_x, args=(angle,)).start()

    elif recieved[0] == "sety":
        angle = int(recieved[1])
        threading.Thread(target=board.set_servo_y, args=(angle,)).start()

    elif recieved[0] == "laser":
        value = int(recieved[1])
        board.set_laser(value)

    elif recieved[0] == "message":
        print(recieved)
    else:
        print("Invalid Message")

            
if __name__ == "__main__":

    # Server
    try:
        MQTT_IPADDR = input("Input Server IP Address: ")
        mqtt_client_cam = MQTT_Publisher(MQTT_IPADDR, MQTT_TOPIC_CAM)
        mqtt_client_controls = MQTT_Subscriber(MQTT_IPADDR, MQTT_TOPIC_PI_ZERO_CONTROLS, control_data_callback)
        mqtt_client_cam.loop_start()
        mqtt_client_controls.loop_start()
    except Exception as e:
        print(f"Failed to connect to MQTT Broker: {e}")
        sys.exit(1)

    # Picam
    try:
        picam = PiCameraInterface()
        picam.start()
    except Exception as e:
        print(f"Error starting PiCamera: {e}")
        print("Quitting...")
        sys.exit()

    # Send camera feed 12 times a second
    fps_controller = FPSLimiter()
    startTime = time.time()

    while global_data["is_running"]:
        fps_controller.startFrame()

        # Send camera feed to server
        frame = picam.getFrame()
        frame_bytes = convert_frame_to_bytes(frame)
        mqtt_client_cam.send(frame_bytes)

        fps_controller.endFrame()

    mqtt_client_cam.loop_stop()
    mqtt_client_cam.disconnect()
    mqtt_client_controls.loop_stop()
    mqtt_client_controls.disconnect()

    board.close()
    picam.close()

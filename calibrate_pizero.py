from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.MQTT import MQTT_TOPIC_CAM, MQTT_TOPIC_CONTROLS, MQTT_IPADDR
from helper.utils import convert_frame_to_bytes
from helper.RaspberryPiZero2 import RaspberryPiZero2
from helper.PyFirmataInterface import PyFirmataInterface
from helper.FPSLimiter import FPSLimiter
from helper.PiCameraInterface import PiCameraInterface

import time



global_data = {
    "is_running": True,
    "is_arduino": True
}

if global_data["is_arduino"]:
    arduino = PyFirmataInterface("")
else:   
    pizero = RaspberryPiZero2()

def control_data_callback(client, userdata, msg):
    recieved: str = msg.payload.decode()
    # Only valid messages should be recieved, so no need to make checks
    recieved = recieved.split(":")
    if recieved[0] == "quit":
        global_data["global_data"] = False

    elif recieved[0] == "turnx":
        angle = int(recieved[1])
        if global_data["is_arduino"]:
            arduino.turn_servo_x(angle)
        else:
            pizero.turn_servo_x(angle)

    elif recieved[0] == "turny":
        angle = int(recieved[1])
        if global_data["is_arduino"]:
            arduino.turn_servo_y(angle)
        else:
            pizero.turn_servo_y(angle)

    elif recieved[0] == "setx":
        angle = int(recieved[1])
        if global_data["is_arduino"]:
            arduino.set_servo_x(angle)
        else:
            pizero.set_servo_x(angle)

    elif recieved[0] == "sety":
        angle = int(recieved[1])
        if global_data["is_arduino"]:
            arduino.set_servo_y(angle)
        else:
            pizero.set_servo_y(angle)

    elif recieved[0] == "laser":
        value = int(recieved[1])
        if global_data["is_arduino"]:
            arduino.set_laser(value)
        else:
            pizero.set_laser(value)

    elif recieved[0] == "message":
        print(recieved)
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
    mqtt_client_cam.loop_start()
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
        if currentTime - startTime > 60 or not global_data["global_data"]:
            break

        fps_controller.endFrame()

    mqtt_client_cam.loop_stop()
    mqtt_client_cam.disconnect()
    mqtt_client_controls.loop_stop()
    mqtt_client_controls.disconnect()

    if global_data["is_arduino"]:
        arduino.close()
    else:
        pizero.cleanup()
    picam.close()

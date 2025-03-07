from helper.PiCameraInterface import PiCameraInterface
from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.RefreshRateLimiter import FPSLimiter
from helper.utils import convert_frame_to_bytes
import time

if __name__ == "__main__":
    picam = PiCameraInterface()
    picam.start()

    server_ipaddr = "192.168.29.99"
    
    # The server will be the desktop/rasberry pi
    # mqtt_turn_data = MQTT_Subscriber(server_ipaddr, "pizero/turn")
    mqtt_image_data = MQTT_Publisher(server_ipaddr, "pizero/image")
    
    rrl = FPSLimiter(12)
    start = time.time()
    
    while True:
        rrl.startFrame()
        
        frame = picam.getFrame()
        image_data = convert_frame_to_bytes(frame)
        mqtt_image_data.send(image_data)

        now = time.time()
        if (now - start > 10):
            break
        
        rrl.endFrame()()

    mqtt_image_data.disconnect()
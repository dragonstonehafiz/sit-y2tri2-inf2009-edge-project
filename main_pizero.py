from helper.PiCameraInterface import PiCameraInterface
from helper.MQTT import MQTT_Publisher, MQTT_Subscriber
from helper.RefreshRateLimiter import RefreshRateLimiter
from helper.utils import convert_frame_to_bytes

if __name__ == "__main__":
    picam = PiCameraInterface()
    picam.start()
    
    # The server will be the desktop/rasberry pi
    mqtt_turn_data = MQTT_Subscriber("localhost", "pizero/turn")
    mqtt_image_data = MQTT_Publisher("localhost", "pizero/image")
    
    rrl = RefreshRateLimiter(12)
    
    while True:
        rrl.startFrame()
        
        frame = picam.capture()
        image_data = convert_frame_to_bytes(frame)
        mqtt_image_data.send(image_data)
        
        rrl.limit()
        
        
from helper.MQTT import MQTT_Publisher
from helper.PiCameraInterface import PiCameraInterface
from helper.RaspberryPiZero2 import RaspberryPiZero2

class AppData:
    mqtt_client_image: MQTT_Publisher
    picam: PiCameraInterface
    pizero: RaspberryPiZero2

    def __init__(self):
        IPADDR = "192.168.29.99"
        self.mqtt_client_image = MQTT_Publisher("", "pizero/image")
        self.picam = PiCameraInterface((240, 240))
        self.pizero = RaspberryPiZero2()

    def quit(self):
        self.picam.close()
        self.pizero.cleanup()
        self.mqtt_client_image.disconnect()

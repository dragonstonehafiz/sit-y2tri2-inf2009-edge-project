import paho.mqtt.client as mqtt
from typing import Callable

class MQTT_Publisher:
    _topic: str
    
    def __init__(self, broker: str, topic: str):
        self._client = mqtt.Client(client_id="Publisher")
        self._topic = topic
        self._client.connect(broker, 1883)
    
    def send(self, payload: any):
        print("here")
        self._client.publish(self._topic, payload)
            
class MQTT_Subscriber:
    
    def __init__(self, broker: str, topic: str, msg_callback: Callable[[mqtt.Client, any, mqtt.MQTTMessage], None]):
        self._client = mqtt.Client()
        self._client.connect(broker, 1883)
        self._client.subscribe(topic)
        self._client.on_message = msg_callback
    
    
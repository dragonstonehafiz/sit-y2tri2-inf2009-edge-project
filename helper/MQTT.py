import paho.mqtt.client as mqtt
from typing import Callable

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker.")

def on_connect_fail(client, userdata, flags, rc):
    print("Could not connect to broker.")

class MQTT_Publisher:
    _topic: str
    
    def __init__(self, broker: str, topic: str):
        self._topic = topic
        self._client = mqtt.Client(client_id="Publisher")
        self._client.on_connect = on_connect
        self._client.on_connect_fail = on_connect_fail
        self._client.connect(broker, 1883)
    
    def send(self, payload: any):
        self._client.publish(self._topic, payload)

    def disconnect(self):
        self._client.disconnect()
            
class MQTT_Subscriber:
    
    def __init__(self, broker: str, topic: str, msg_callback: Callable[[mqtt.Client, any, mqtt.MQTTMessage], None]):
        self._client = mqtt.Client()
        self._client.connect(broker, 1883)
        self._client.on_connect = on_connect
        self._client.on_connect_fail = on_connect_fail
        self._client.on_message = msg_callback
        self._client.subscribe(topic)

    def loop_start(self):
        """Call before main loop"""
        self._client.loop_start()

    def loop_stop(self):
        """Call at end of program"""
        self._client.loop_stop()

    def disconnect(self):
        self._client.disconnect()
    
    
import paho.mqtt.client as mqtt
from typing import Callable

MQTT_TOPIC_CAM = "pizero/cam"
"""topic that pizero will send image data to"""

MQTT_TOPIC_PI_ZERO_CONTROLS = "pizero/controls"
"""topic that server will send control data to"""

MQTT_TOPIC_SERVER_CONTROLS = "server/controls"
"""topic that pi zero will send server controls to"""

def on_connect(client, userdata, flags, rc):
    print(f"{client._client_id.decode() if client._client_id else 'Unknown'} successfully connected to Broker.")

def on_connect_fail(client, userdata, flags, rc):
    print("Could not connect to broker.")

class MQTT_Publisher:
    _topic: str
    
    def __init__(self, broker: str, topic: str):
        self._topic = topic
        self._client = mqtt.Client(client_id=f"{topic} sublisher")
        self._client.on_connect = on_connect
        self._client.on_connect_fail = on_connect_fail
        self._client.connect(broker, 1883)

    def loop_start(self):
        """Call before main loop"""
        self._client.loop_start()

    def loop_stop(self):
        """Call at end of program"""
        self._client.loop_stop()
    
    def send(self, payload: any):
        self._client.publish(self._topic, payload)

    def disconnect(self):
        self._client.disconnect()
            
class MQTT_Subscriber:
    
    def __init__(self, broker: str, topic: str, msg_callback: Callable[[mqtt.Client, any, mqtt.MQTTMessage], None]):
        self._client = mqtt.Client(client_id=f"{topic} subscriber")
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
    
    
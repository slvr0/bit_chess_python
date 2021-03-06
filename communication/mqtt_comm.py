
import paho.mqtt.client as mqtt

MQTT_BROKER_HOST = 'localhost'
MQTT_BROKER_PORT = 1883
MQTT_KEEP_ALIVE_INTERVAL = 60

import paho.mqtt.client as mqtt


# def on_connect(client, userdata, flags, rc):
#   print("Connected with result code " + str(rc))
#
#
# def on_message(client, userdata, msg):
#   print(msg.topic + " " + str(msg.payload))
#
#
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.connect("localhost", 1883, 60)
# client.subscribe("mqtt_test")
# client.loop_forever()

class Subscriber() :

  def __init__(self, topic, host_name = MQTT_BROKER_HOST, host_port = MQTT_BROKER_PORT):
    self.client = mqtt.Client()

    self.topic = topic
    self.host_name = host_name
    self.host_port = host_port

    self.client.on_connect = self.on_conn
    self.client.on_message = self.on_message

    self.client.connect("localhost", 1883, 60)

    self.client.subscribe(self.topic)

    self.client.loop_forever()

  def on_conn(self, client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

  def on_message(self, client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))







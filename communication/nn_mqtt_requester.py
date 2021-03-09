
from communication.mqtt_comm import Subscriber
from nn.keras_net import KerasNet
import paho.mqtt.client as mqtt
from core.chess_board import ChessBoard
from core.move_generator import MoveGenerator

MQTT_BROKER_HOST = 'localhost'
MQTT_BROKER_PORT = 1883
MQTT_KEEP_ALIVE_INTERVAL = 60

from nn.data_parser import NN_DataParser
class NN_MQTT_Requester() :
  def __init__(self, topic, response_topic, move_gen, host_name = MQTT_BROKER_HOST, host_port = MQTT_BROKER_PORT):

    self.client = mqtt.Client()

    self.topic = topic
    self.host_name = host_name
    self.host_port = host_port

    self.client.on_connect = self.on_conn
    self.client.on_message = self.on_message

    self.client.connect("localhost", 1883, 60)

    self.client.subscribe(self.topic)

    self.move_gen = move_gen

    self.response_topic = response_topic

    self.nn_parser = NN_DataParser()

    input_dim = (13, 64)
    output_dim = self.nn_parser.output_dims

    self.ac_net = KerasNet(13 * 64, output_dim, 'net_0')
    self.graph = self.ac_net.load_model(on_thread=True)

    self.publisher = mqtt.Client()

    self.publisher.connect("localhost", 1883, 60)

  def on_conn(self, client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

  def start_on_thread(self):
    self.client.loop_forever()

  def on_message(self, client, userdata, msg):
    #self.client.publish('mcts_cache_position', msg.payload)

    forward_message = str(msg.payload.decode())

    cb = ChessBoard(forward_message)

    actions = self.move_gen.get_legal_moves(cb)

    nn_idcs = [self.nn_parser.nn_move(m) for m in actions]

    tensor_data = self.nn_parser.nn_board(cb)

    with self.graph.as_default() :
      net_logs = self.ac_net.predict(tensor_data.flatten())

    log_mult = 1 if cb.white_to_act else -1

    net_logs = [v*log_mult for i,v in enumerate(net_logs[0]) if i in nn_idcs]

    forward_message += " {"
    for idx, log in zip(nn_idcs, net_logs) :

        forward_message += "{0}:{1:1f}:".format(int(idx),log)
    forward_message = forward_message[:-1] + "}"

    self.client.publish(self.response_topic, forward_message.encode('utf-8'))


def nn_mqtt_req_on_thread(topic, response_topic, move_gen, host_name = MQTT_BROKER_HOST, host_port = MQTT_BROKER_PORT) :
  nn_mqtt_req = NN_MQTT_Requester(topic, response_topic, move_gen, host_name, host_port)

  nn_mqtt_req.client.loop_forever()


















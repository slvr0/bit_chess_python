
from core.chess_board import ChessBoard
from mcts.cached_mcts_positions import CachedMCTSPositions

import paho.mqtt.client as mqtt

import time

class NNMCTSPipe :
  def __init__(self, cached_positions, publisher_topic = "mcts_tree_init"):

    self.cached_positions = cached_positions
    self.publisher_topic = publisher_topic

    self.collected_data = []
    self.wait_time = 60

    self.publisher = mqtt.Client()
    self.publisher.connect('localhost' ,1883, self.wait_time)

  def log_and_return_mcts_response(self, cb, net, nn_parser, graph) :

    pos_key = cb.get_zobrist()
    t0 = time.time()

    ret = False
    timeout = 0

    #request c++ to start evaluating position. once done it will be sent back and added to cached positions
    self.publisher.publish(self.publisher_topic, cb.get_fen())

    pos = 0

    while not ret :  #or timeout <= self.wait_time :
      ret, pos = self.cached_positions.get(pos_key)

      timeout = time.time() - t0



    print("found position! nice!")
    return pos


  def send_for_training(self):
    return self.collected_data

  def flush_collected_data(self):
    self.collected_data = []


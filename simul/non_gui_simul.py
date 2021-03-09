import torch as T
import torch.nn.functional as F

from core.chess_board import ChessBoard
from core.chess_move import ChessMove
import os
from core.move_generator import MoveGenerator
import numpy as np

from nn.keras_net import KerasNet
from nn import actor_critic_network
from nn import data_parser
from nn import nn_output_values
from nn import nn_params
from wrappers.chess_env import ChessEnvironment

from core.utils import board_notations

from nn.NNMCTSPipe import NNMCTSPipe

import tensorflow as tf

class NonGUISimulationEnvironment :
  def __init__(self, on_thread = False):
    self.move_gen = MoveGenerator()
    self.env = ChessEnvironment(self.move_gen)

    self.nn_parser = data_parser.NN_DataParser()

    input_dim = (13, 64)
    output_dim = self.nn_parser.output_dims

    self.on_thread = on_thread
    # self.ac_net = actor_critic_network.ActorCriticNetwork(input_dim, output_dim, 'ac_global')
    # self.ac_net.load_network()

    self.ac_net = KerasNet(13 * 64, output_dim, 'net_0')

    if on_thread :
      self.graph = self.ac_net.load_model(on_thread=True)
    else :
      self.ac_net.load_model()

      self.sess = None
      self.graph = None

    self.game_folder_path = "simul/test_games"

  @staticmethod
  def start_game(cb, move_gen, cached_positions, game_id, on_thread = False):

    env = ChessEnvironment(move_gen)

    nn_mcts_pipe = NNMCTSPipe(cached_positions)

    nn_parser = data_parser.NN_DataParser()

    input_dim = (13, 64)
    output_dim = nn_parser.output_dims

    on_thread = on_thread
    # self.ac_net = actor_critic_network.ActorCriticNetwork(input_dim, output_dim, 'ac_global')
    # self.ac_net.load_network()

    ac_net = KerasNet(13 * 64, output_dim, 'net_0')

    if on_thread:
      graph = ac_net.load_model(on_thread=True)
    else:
      ac_net.load_model()
      graph = None

    game_folder_path = "simul/test_games"

    fp = os.path.join(game_folder_path, str(game_id) + ".txt")

    n_games = 1000

    def make_move(env, nn_mcts_pipe, mcts_support = False) :
      actions = env.get_legal_moves()
      status, reward, to_act, terminal, repeats = env.get_board_info(actions)

      if terminal:  return status, reward, terminal

      if mcts_support :
        bot_choose = nn_mcts_pipe.log_and_return_mcts_response(env.cb, ac_net, nn_parser, graph)
      else :
        bot_choose = NonGUISimulationEnvironment.bot_choose_move(actions, ac_net, env, nn_parser, graph)

      #record it
      NonGUISimulationEnvironment.record_move(file, to_act, actions, bot_choose)

      #update the gamestate
      env.step(actions, bot_choose)

      return status, reward, terminal

    env.reset(cb)

    mcts_bot_color = env.cb.white_to_act

    for game in range(n_games) :
      env.reset(cb)

      with open(fp, '+w') as file :
        while True:
          status, reward, terminal = make_move(env, nn_mcts_pipe, mcts_support=True)
          if terminal : break

          status, reward, terminal = make_move(env, nn_mcts_pipe, mcts_support=False)
          if terminal: break

  @staticmethod
  def pgn_convert(self, move, env):
    white_toact = self.env.cb.white_to_act

  @staticmethod
  def bot_choose_move(actions, net, env, nn_parser, graph = None):

    board_vec = nn_parser.nn_board(env.cb)

    if graph is None :
      net_logits = net.predict(board_vec.flatten())
    else:
      with graph.as_default():
        net_logits = net.predict(board_vec.flatten())

    moves_prob = []
    for action in actions :

      nn_id = nn_parser.nn_move(action)

      moves_prob.append(net_logits[0, nn_id])

    optimal_move = np.argmax(moves_prob)

    return optimal_move

  @staticmethod
  def record_move(file, to_act, actions, bot_choose):
    if not to_act:
      bn = board_notations[::-1]
    else:
      bn = board_notations

    m = actions[bot_choose]

    if m.ptype == 'P':
      file.write(bn[m._from].lower() + bn[m.to].lower())
    else:
      file.write(m.ptype.lower() + bn[m._from].lower() + bn[m.to].lower())
    file.write(" ")


    #things to check
    # castle, enp, promo, capture squares, checking king, move to is occupied? (x)


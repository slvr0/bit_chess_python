import torch as T
import torch.nn.functional as F

from core.chess_board import ChessBoard
from core.chess_move import ChessMove
import os
from core.move_generator import MoveGenerator
import numpy as np

from nn import actor_critic_network
from nn import data_parser
from nn import nn_output_values
from nn import nn_params
from wrappers.chess_env import ChessEnvironment

from core.utils import board_notations

class NonGUISimulationEnvironment :
  def __init__(self):
    self.move_gen = MoveGenerator()
    self.env = ChessEnvironment(self.move_gen)

    self.nn_parser = data_parser.NN_DataParser()

    input_dim = (13, 64)
    output_dim = self.nn_parser.output_dims

    self.ac_net = actor_critic_network.ActorCriticNetwork(input_dim, output_dim, 'ac_global')
    self.ac_net.load_network()

    self.game_folder_path = "simul/test_games"

  def start_game(self, cb, game_id):
    fp = os.path.join(self.game_folder_path, str(game_id) + ".txt")

    self.env.reset(cb)

    with open(fp, '+w') as file :
      while True:
        #check valid moves, take action from
        actions = self.env.get_legal_moves()
        status, reward, to_act, terminal, repeats = self.env.get_board_info(actions)

        #self.env.cb.print_console()

        #actions.print()
        if terminal :  break


        #ask bot what he wants to play
        bot_choose = self.bot_choose_move(actions)

        #record it
        self.record_move(file, to_act, actions, bot_choose)

        #update the gamestate
        self.env.step(actions, bot_choose)

  def pgn_convert(self, move):
    white_toact = self.env.cb.white_to_act

  def bot_choose_move(self, actions):
    board_vec = self.nn_parser.nn_board(self.env.cb)

    board_vec = board_vec.flatten()
    board_tensor = T.FloatTensor([board_vec])

    net_logits, net_value = self.ac_net(board_tensor)

    moves = self.move_gen.get_legal_moves(self.env.cb)

    policy = F.normalize(net_logits, dim=1)[0]

    #map policy probabilities to moves
    moves_prob = []
    for move in moves :
      nn_id = self.nn_parser.nn_move(move)

      moves_prob.append(policy[nn_id].item())

    optimal_move = np.argmax(moves_prob)

    return optimal_move

  def record_move(self, file, to_act, actions, bot_choose):
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


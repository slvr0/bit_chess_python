
from core.chess_board import ChessBoard
from core.chess_move import ChessMove

from core.move_generator import MoveGenerator

from nn import actor_critic_network
from nn import data_parser
from nn import nn_output_values
from nn import nn_params

import torch as T
import torch.nn.functional as F

from wrappers.chess_env import ChessEnvironment

class GUI_Logic :
  def __init__(self):

    self.move_gen = MoveGenerator()
    self.env = ChessEnvironment(self.move_gen)

    standard_position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    cb = ChessBoard(standard_position)

    self.env.reset(cb)

    self.nn_parser = data_parser.NN_DataParser()

    input_dim = (13,64)
    output_dim = self.nn_parser.output_dims

    self.ac_net = actor_critic_network.ActorCriticNetwork(input_dim, output_dim, 'ac_global')
    self.ac_net.load_network()

  def query_legal_move(self, id_from, id_to) :
    moves = self.env.get_legal_moves()

    match_move = [midx for midx, move in enumerate(moves) if move._from == id_from and move.to == id_to]

    if len(match_move) == 0 :  return False
    elif len(match_move) == 1 :
      #internally update the board representation
      midx = match_move[0]
      self.env.step(moves, midx)
      return True

  def query_computer_move(self):
    cb = self.env.cb

    board_vec = self.nn_parser.nn_board(cb)

    board_vec = board_vec.flatten()
    board_tensor = T.FloatTensor([board_vec])

    net_logits, net_value = self.ac_net(board_tensor)

    moves = self.move_gen.get_legal_moves(cb)

    legal_idcs = []
    nn_move_dict_translate = dict()

    for midx, move in enumerate(moves) :
      nn_idx = self.nn_parser.nn_move(move)

      nn_move_dict_translate[nn_idx] = midx
      legal_idcs.append(nn_idx)

    for i in range(self.nn_parser.output_dims):
      if i not in legal_idcs :
        net_logits[0][i] = 0.0

    policy = F.softmax(net_logits, dim=1)
    action = T.argmax(policy).item()

    if(T.max(policy).item()) == 0.0 :
      print("this bot got no clue")
      optim_move_idx = nn_move_dict_translate[action]
      moves[optim_move_idx].print()

      self.env.step(moves, optim_move_idx)

      choosen_move = moves[optim_move_idx]

      return choosen_move._from, choosen_move.to

    else:

      print(nn_move_dict_translate.keys())


      optim_move_idx = nn_move_dict_translate[action]


      moves[optim_move_idx].print()

      self.env.step(moves, optim_move_idx)

      choosen_move = moves[optim_move_idx]

      return choosen_move._from, choosen_move.to








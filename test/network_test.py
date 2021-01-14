
from core.chess_board import ChessBoard
from core.utils import *
from nn.data_parser import NN_DataParser, nn_action_space
from nn.nn_output_values import *
from nn.nn_params import hyperparams
from nn.actor_critic_network import ActorCriticNetwork
from wrappers.chess_env import ChessEnvironment

from mcts.tree_node import MCTS_node
from mcts.mcts_search import MCTS_Search
from mcts.rollout import MCTS_Rollout

import torch as T
import torch.nn.functional as F
import torch.nn as nn

def run_network_test(nn_dp, move_gen) :

  #1 setup a bord position. make a node with it. parse it through the node parser. imput info to network.
  #make this work. end of day

  sp = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  cb = ChessBoard(sp)

  env = ChessEnvironment(move_gen)

  node = MCTS_node(0, cb)

  node.expand(env)

  board_vec, norm_branch_scores, branch_nn_indexes, terminal = nn_dp.nn_mcts_node(node)

  # print(board_vec)
  # print(norm_branch_scores)
  # print(branch_nn_indexes)
  # print(terminal)

  #now network setup

  input_dim = (13,64)
  output_dim = nn_dp.output_dims

  ac_net = ActorCriticNetwork(input_dim=input_dim, output_dim=output_dim, network_name='ac_test_0')

  board_vec = board_vec.flatten()
  board_tensor = T.FloatTensor([board_vec])

  logits, value = ac_net(board_tensor)

  print(type(branch_nn_indexes))

  legal_index_tensor = T.LongTensor([branch_nn_indexes])[0]

  logits = logits[0]
  value = value[0]

  logits_vals = T.index_select(logits, 0, legal_index_tensor)

  print(logits_vals, value.item())








from nn.nn_output_values import nn_action_space, nn_action_space_list
from core.utils import board_notations

import numpy as np

#converts information from chessboard or mcts node to neural net data input/output
class NN_DataParser :
  def __init__(self):
    self.output_dims = len(nn_action_space_list)

  def move_nn(self, idx):
    return nn_action_space_list[idx]

  def nn_move(self, move):
    _from = move._from
    to = move.to
    promo = move.promotion
    if promo == '' :
      key = board_notations[_from].lower() + board_notations[to].lower()
      assert key in nn_action_space.keys()

      return nn_action_space[key]

    else :
      key =  board_notations[_from].lower() + board_notations[to].lower()  + promo.lower()

      assert key in nn_action_space.keys()

      return nn_action_space[key]

  #returns vectors of size 13x64, make use of scipy????
  def nn_board(self, cb):
    #dim 0, idx 0-11 = pieces . idx 12 = boardstate , wc00, wc000, bc00, bc000, white_turn ,enp_flag
    return cb.as_nn_tensor()

  def nn_mcts_node(self, node):
    board_tensor = self.nn_board(node.cb)

    #terminal data
    terminal = node.terminal

    #childs, each childs move idx, and their score value

    #score values
    branch_scores = np.zeros( shape=(len(node.childs)) )
    branch_nn_indexes = np.zeros( shape=(len(node.childs)) ,dtype=np.int )

    for index, child in enumerate(node.childs) :
      branch_scores[index] = child.get_eval_score()
      branch_nn_indexes[index] = self.nn_move(child.from_action)

    #normalized_branch_scores
    norm = np.linalg.norm(branch_scores)
    norm_branch_scores = branch_scores * norm

    return board_tensor, norm_branch_scores, branch_nn_indexes, terminal
















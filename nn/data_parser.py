
from nn.nn_output_values import nn_action_space, nn_action_space_list
from core.utils import board_notations
from core.chess_board import ChessBoard
import numpy as np
from decimal import *

#converts information from chessboard or mcts node to neural net data input/output
class NN_DataParser :
  def __init__(self):
    self.output_dims = len(nn_action_space_list)

  def decode_boardtensor(self, boardtensor):
    cb = ChessBoard()
    #boardtensor = np.zeros(13,64)
    for idx_i, _ in enumerate(boardtensor) :

      for idx_j, v in enumerate(boardtensor[idx_i]) :
        if v == 1 :

          if idx_i == 0 : cb.pawns_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 1 : cb.knights_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 2 : cb.bishops_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 3 : cb.rooks_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 4 : cb.queens_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 5 : cb.king_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 6 : cb.enemy_pawns_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 7 : cb.enemy_knights_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 8 : cb.enemy_bishops_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 9 : cb.enemy_rooks_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 10 : cb.enemy_queens_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 11 : cb.enemy_king_ |= np.uint(1) << np.uint(idx_j)
          elif idx_i == 12 : pass #TBD game info

    return cb

  def decode_training_batch(self, training_data) :
    board_tensor = training_data.board_tensor
    logits = training_data.logits
    logits_idc = training_data.logits_idcs

    print("--BOARD--")

    self.decode_boardtensor(board_tensor).print_console()

    print("--MCTS GROUND TRUTH-- (simulation output)")

    for i, idc in enumerate(logits_idc) :
      print(nn_action_space_list[idc], "=", int(logits[i] * 100) / 100.0)


    #   dv = abs(logits[idc] - network_output[idc])
    #   total_dt += dv
    # print(total_dt)


  def decode_training_data(self, board_tensor, logits, logits_idc, value, orig_value, network_output):
    # print("--BOARD--")
    #
    # self.decode_boardtensor(board_tensor).print_console()
    #
    # print("--MCTS GROUND TRUTH-- (simulation output)")
    #

    total_dt = 0
    for idc in logits_idc :
      #print(nn_action_space_list[idc], "=", int(logits[idc] * 100) / 100.0)

      dv = abs(logits[idc] - network_output[idc])
      total_dt += dv
    print(total_dt)

    # print("--VALUE--")
    # print(value, orig_value)

    # print("--NETWORK PREDICTS")
    #
    # for idc in logits_idc:
    #   print(nn_action_space_list[idc], "=", int(network_output[idc] * 100) / 100.0, " ", end="")

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
















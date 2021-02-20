from core.chess_board import ChessBoard
from core.chess_square import Square, idx_to_row_col, row_col_to_idx
from core.chess_attack_tables import IndexedKnightAttacks, \
  IndexedPawnAttacks, RookMagicBitboard, SlidingAttackTables, BishopMagicBitboard
from core.move_generator import MoveGenerator
import numpy as np
from core.utils import CombinationSolver, BinaryHelper

def IS_EQ(v, comp) :
  assert v == comp

def IS_GREATER(v, comp) :
  assert v > comp

def IS_LOWER(v, comp) :
  assert v < comp

def IS_NOT_IN(v, comp = []):
  try:
    for compval in comp :
      assert v != compval
  except ValueError as ve:
    print(ve)

#compare list output, is equal only if all elements are equal
def IS_EQUAL_LIST(vl, comp = []):
  assert len(vl) == len(comp)

  for v in vl :
    assert v in comp

def run_move_generator_test(move_gen) :

  # sp6 = '1r1k1p2/1P4P1/8/8/8/8/2R5/1K6 w - - 0 1'
  # cb6 = ChessBoard(fen_position=sp6)
  #
  # moves = move_gen.get_legal_moves(cb6)
  #
  # n_moves_correct = 26
  # try :
  #   IS_EQ(len(moves), n_moves_correct)
  # except:
  #   print("error in test 5 , output : {} , correct : {}".format(len(moves), n_moves_correct))
  #
  #
  # sp7 = '1r1k1p2/1P4P1/8/8/8/5b2/2R3P1/1K6 w - - 0 1'
  # cb6 = ChessBoard(fen_position=sp7)
  #
  # moves = move_gen.get_legal_moves(cb6)
  # n_moves_correct = 27
  # try :
  #   IS_EQ(len(moves), n_moves_correct)
  # except:
  #   print("error in test 6 , output : {} , correct : {}".format(len(moves), n_moves_correct))
  #
  # sp8 = '1kq3R1/8/5B2/8/8/8/2K5/8 w - - 0 1'
  # cb6 = ChessBoard(fen_position=sp8)
  #
  # moves = move_gen.get_legal_moves(cb6)
  # n_moves_correct = 8
  # try :
  #   IS_EQ(len(moves), n_moves_correct)
  # except:
  #   print("error in test 7 , output : {} , correct : {}".format(len(moves), n_moves_correct))
  #
  # #sp9 = 'r3r1n1/n1pp4/6p1/1p1bpp1p/1q3P2/NP4P1/PRPPP2P/2QK1BNR'
  # #cb9 = ChessBoard(fen_position=sp9)
  # # moves = move_gen.get_legal_moves(cb9)
  # # moves.print()
  #
  # #extensive king testing
  #
  sp_0 = '3r1k2/8/8/5n2/3K4/4P3/8/8 w - - 0 1'
  sp_1 = '6r1/1k6/1p6/K7/8/8/8/8 w - - 0 1'
  sp_2 = '8/4kq2/8/8/8/8/4n3/5Kr1 w - - 0 1'
  sp_3 = 'k7/8/7b/8/5n2/8/3r1p2/3K4 w - - 0 1'
  sp_4 = '4b3/3K4/2n1p3/5q2/8/8/8/7k w - - 0 1'
  sp_5 = '8/5q2/3r2pK/8/8/8/8/7k w - - 0 1'

  sp_6 = '8/8/4k3/3n4/3p4/3Kb3/1NNQ4/8 w - - 0 1'
  sp_7 = '5K2/4nnn1/4nnn1/5k2/8/8/8/8 w - - 0 1'
  sp_8 = '8/8/8/PP6/Pk4PP/5nPP/6PP/2K1qr2 w - - 0 1'
  sp_9 = '5k2/8/3P4/3Knq2/2b5/8/8/8 w - - 0 1'
  sp_10 = 'b7/1b1k4/2b5/3b4/4b3/5R2/6b1/7K w - - 0 1'

  cb = ChessBoard(fen_position=sp_0)
  moves = move_gen.get_legal_moves(cb)

  sp_0_c = 5
  n_moves = len(moves)
  try :
    IS_EQ(n_moves, sp_0_c)
  except:
    print("error in test kingtest 0 , output : {} , correct : {}".format(n_moves, sp_0_c))


  #sp_1 = '6r1/1k6/1p6/K7/8/8/8/8 w - - 0 1'
  cb = ChessBoard(fen_position=sp_1)
  moves = move_gen.get_legal_moves(cb)

  sp_1_c = 3
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_1_c)
  except:
    print("error in test kingtest 1 , output : {} , correct : {}".format(n_moves, sp_1_c))

  cb = ChessBoard(fen_position=sp_2)
  moves = move_gen.get_legal_moves(cb)

  sp_2_c = 1
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_2_c)
  except:
    print("error in test kingtest 2 , output : {} , correct : {}".format(n_moves, sp_2_c))

  cb = ChessBoard(fen_position=sp_3)
  moves = move_gen.get_legal_moves(cb)

  sp_3_c = 2
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_3_c)
  except:
    print("error in test kingtest 3 , output : {} , correct : {}".format(n_moves, sp_3_c))

  cb = ChessBoard(fen_position=sp_4)
  moves = move_gen.get_legal_moves(cb)

  sp_4_c = 4
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_4_c)
  except:
    print("error in test kingtest 4 , output : {} , correct : {}".format(n_moves, sp_4_c))

  cb = ChessBoard(fen_position=sp_5)
  moves = move_gen.get_legal_moves(cb)

  sp_5_c = 1
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_5_c)
  except:
    print("error in test kingtest 5 , output : {} , correct : {}".format(n_moves, sp_5_c))

  cb = ChessBoard(fen_position=sp_6)
  moves = move_gen.get_legal_moves(cb)

  sp_6_c = 11 + 6 + 3 + 3
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_6_c)
  except:
    print("error in test kingtest 6 , output : {} , correct : {}".format(n_moves, sp_6_c))

  cb = ChessBoard(fen_position=sp_7)
  moves = move_gen.get_legal_moves(cb)

  sp_7_c = 1
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_7_c)
  except:
    print("error in test kingtest 7 , output : {} , correct : {}".format(n_moves, sp_7_c))


  cb = ChessBoard(fen_position=sp_8)
  moves = move_gen.get_legal_moves(cb)

  sp_8_c = 2
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_8_c)
  except:
    print("error in test kingtest 8 , output : {} , correct : {}".format(n_moves, sp_8_c))

  cb = ChessBoard(fen_position=sp_9)
  moves = move_gen.get_legal_moves(cb)

  sp_9_c = 2
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_9_c)
  except:
    print("error in test kingtest 9 , output : {} , correct : {}".format(n_moves, sp_9_c))

  cb = ChessBoard(sp_10)
  moves = move_gen.get_legal_moves(cb)

  sp_10_c = 3
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_10_c)
  except:
    print("error in test kingtest 10 , output : {} , correct : {}".format(n_moves, sp_10_c))



  # sp_11 = '8/6k1/8/8/2Q1Q3/8/8/1Q1K4 b - - 1 1'
  # cb = ChessBoard(fen_position=sp_11)
  # cb.mirror_side()
  # moves = move_gen.get_legal_moves(cb)
  #
  # sp_11_c = 4
  # n_moves = len(moves)
  # try:
  #   IS_EQ(n_moves, sp_11_c)
  # except:
  #   print("error in test kingtest 11 , output : {} , correct : {}".format(n_moves, sp_11_c))


  sp12 = '8/6k1/8/8/4Q3/2QQ4/8/3K4 b - - 1 1'
  cb = ChessBoard(fen_position=sp12)
  cb.mirror_side()
  moves = move_gen.get_legal_moves(cb)

  sp_11_c = 4
  n_moves = len(moves)
  try:
    IS_EQ(n_moves, sp_11_c)
  except:
    print("error in test kingtest 12 , output : {} , correct : {}".format(n_moves, sp_11_c))

  # debug positions from mcts errors
  # sp_debug_mcts_0 = 'rn4nr/pp5p/3kpppp/3P4/PPp5/4PBP1/3P1PbP/1NKR3R w K - 0 1'
  # cb = ChessBoard(sp_debug_mcts_0)
  # moves = move_gen.get_legal_moves(cb)
  # moves.print()









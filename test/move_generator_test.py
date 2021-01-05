from chess_board import ChessBoard
from chess_square import Square, idx_to_row_col, row_col_to_idx
from chess_attack_tables import IndexedKnightAttacks, \
  IndexedPawnAttacks, RookMagicBitboard, SlidingAttackTables, BishopMagicBitboard
from move_generator import MoveGenerator
import numpy as np
from utils import CombinationSolver, BinaryHelper

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

def run_move_generator_test() :
  move_gen = MoveGenerator()

  # sp = '8/4K3/8/6N1/4r3/8/2k5/8 w - - 0 1'
  # cb = ChessBoard(fen_position=sp)
  # n_checkers = move_gen.get_enemy_attackinfo(cb)['n_checkers']
  # n_correct = 1
  # try :
  #   IS_EQ(n_checkers, 1)
  # except:
  #   print("error in test 1 , output : {} , correct : {}".format(n_checkers, n_correct))
  #
  # sp2 = '8/4K3/3p4/6N1/4r3/8/2k5/8 w - - 0 1'
  # cb2 = ChessBoard(fen_position=sp2)
  # n_checkers = move_gen.get_enemy_attackinfo(cb2)['n_checkers']
  # n_correct = 2
  # try :
  #   IS_EQ(n_checkers, n_correct)
  # except:
  #   print("error in test 2 , output : {} , correct : {}".format(n_checkers, n_correct))
  #
  # sp2 = '8/4K3/3p4/6N1/4r2b/8/2k5/8 w - - 0 1'
  # cb2 = ChessBoard(fen_position=sp2)
  # n_checkers = move_gen.get_enemy_attackinfo(cb2)['n_checkers']
  # n_correct = 2
  # try :
  #   IS_EQ(n_checkers, n_correct)
  # except:
  #   print("error in test 3 , output : {} , correct : {}".format(n_checkers, n_correct))
  #
  # sp2 = '8/1q2K3/3p4/6N1/4r2b/8/2k5/8 w - - 0 1'
  # cb2 = ChessBoard(fen_position=sp2)
  # n_checkers = move_gen.get_enemy_attackinfo(cb2)['n_checkers']
  # n_correct = 3
  # try :
  #   IS_EQ(n_checkers, n_correct)
  # except:
  #   print("error in test 4 , output : {} , correct : {}".format(n_checkers, n_correct))

  sp4 = '5k2/8/8/3Pp3/3K4/8/8/8 w - e6 0 2'
  cb4 = ChessBoard(fen_position=sp4)
  move_gen.generate_legal_moves(cb4)

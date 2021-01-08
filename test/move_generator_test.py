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

  sp = '8/4K3/8/6N1/4r3/8/2k5/8 w - - 0 1'
  cb = ChessBoard(fen_position=sp)
  n_checkers = move_gen.get_enemy_attackinfo(cb)['n_checkers']
  n_correct = 1
  try :
    IS_EQ(n_checkers, 1)
  except:
    print("error in test 1 , output : {} , correct : {}".format(n_checkers, n_correct))

  sp2 = '8/4K3/3p4/6N1/4r3/8/2k5/8 w - - 0 1'
  cb2 = ChessBoard(fen_position=sp2)
  n_checkers = move_gen.get_enemy_attackinfo(cb2)['n_checkers']
  n_correct = 1
  try :
    IS_EQ(n_checkers, n_correct)
  except:
    print("error in test 2 , output : {} , correct : {}".format(n_checkers, n_correct))

  sp2 = '8/4K3/3p4/6N1/4r2b/8/2k5/8 w - - 0 1'
  cb2 = ChessBoard(fen_position=sp2)
  n_checkers = move_gen.get_enemy_attackinfo(cb2)['n_checkers']
  n_correct = 1
  try :
    IS_EQ(n_checkers, n_correct)
  except:
    print("error in test 3 , output : {} , correct : {}".format(n_checkers, n_correct))

  sp2 = '8/1q2K3/3p4/6N1/4r2b/8/2k5/8 w - - 0 1'
  cb2 = ChessBoard(fen_position=sp2)
  n_checkers = move_gen.get_enemy_attackinfo(cb2)['n_checkers']
  n_correct = 2
  try :
    IS_EQ(n_checkers, n_correct)
  except:
    print("error in test 4 , output : {} , correct : {}".format(n_checkers, n_correct))

  sp6 = '1r1k1p2/1P4P1/8/8/8/8/2R5/1K6 w - - 0 1'
  cb6 = ChessBoard(fen_position=sp6)

  moves = move_gen.generate_legal_moves(cb6)
  n_moves_correct = 26
  try :
    IS_EQ(len(moves), n_moves_correct)
  except:
    print("error in test 5 , output : {} , correct : {}".format(len(moves), n_moves_correct))

  sp7 = '1r1k1p2/1P4P1/8/8/8/5b2/2R3P1/1K6 w - - 0 1'
  cb6 = ChessBoard(fen_position=sp7)

  moves = move_gen.generate_legal_moves(cb6)
  n_moves_correct = 27
  try :
    IS_EQ(len(moves), n_moves_correct)
  except:
    print("error in test 6 , output : {} , correct : {}".format(len(moves), n_moves_correct))

  sp8 = '1kq3R1/8/5B2/8/8/8/2K5/8 w - - 0 1'
  cb6 = ChessBoard(fen_position=sp8)

  moves = move_gen.generate_legal_moves(cb6)
  n_moves_correct = 8
  try :
    IS_EQ(len(moves), n_moves_correct)
  except:
    print("error in test 6 , output : {} , correct : {}".format(len(moves), n_moves_correct))












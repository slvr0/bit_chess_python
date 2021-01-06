from core.chess_board import ChessBoard
from core.chess_square import Square, idx_to_row_col, row_col_to_idx
from core.chess_attack_tables import IndexedKnightAttacks, \
  IndexedPawnAttacks, RookMagicBitboard, SlidingAttackTables, BishopMagicBitboard
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

def run_attack_tables_test(move_gen):

  attack_tables = move_gen.sliding_attacktables

  #---#
  sp = 'rnbqk1nr/pppp2pp/3bp3/5p2/P4B2/2NP4/1PP1PPPP/R2QKBNR b KQkq - 1 4'
  cb = ChessBoard(fen_position=sp)
  occ = cb.get_all_pieces() | cb.get_all_pieces(ours=False)
  attack_squares = attack_tables.query_rook_attacks(1, occ)

  b1 = BinaryHelper.create_bin_from_int_list([0, 2, 3, 9])
  try :
    IS_EQ(attack_squares, b1)
  except:
    print('failed on test 1, output : {}, compare : {}'.format(attack_squares, b1))

  #---#
  sp2 = 'rnbqk1nr/pppp2pp/3bp3/8/P3p3/2NP4/1PP2PPP/R1BQKBNR w KQkq - 0 5'
  cb = ChessBoard(fen_position=sp2)
  occ = cb.get_all_pieces() | cb.get_all_pieces(ours=False)
  attack_squares2 = attack_tables.query_rook_attacks(29, occ)

  b2 = BinaryHelper.create_bin_from_int_list([28, 37, 45, 53, 61, 21, 13, 30, 31])
  try :
    IS_EQ(attack_squares2, b2)
  except:
    print('failed on test 2, output : {}, compare : {}'.format(attack_squares2, b2))

  #---#
  sp3 = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  cb = ChessBoard(fen_position=sp3)
  occ = cb.get_all_pieces() | cb.get_all_pieces(ours=False)
  attack_squares3 = attack_tables.query_bishop_attacks(2, occ)
  b3 = BinaryHelper.create_bin_from_int_list([9, 11])
  try :
    IS_EQ(attack_squares3, b3)
  except:
    print('failed on test 3, output : {}, compare : {}'.format(attack_squares3, b3))

  # ---#
  sp4 = 'rnbqkbnr/ppp1pp1p/6p1/3p4/1P6/8/PBPPPPPP/RN1QKBNR w KQkq - 0 3'
  cb = ChessBoard(fen_position=sp4)
  occ = cb.get_all_pieces() | cb.get_all_pieces(ours=False)
  attack_squares4 = attack_tables.query_bishop_attacks(9, occ)
  b4 = BinaryHelper.create_bin_from_int_list([0, 16,2,18, 27, 36, 45, 54, 63])
  try:
    IS_EQ(attack_squares4, b4)
  except:
    print('failed on test 4, output : {}, compare : {}'.format(attack_squares4, b4))








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

  sp = '2k5/8/3n4/8/8/8/8/R1K5 w Q - 0 1'
  # ---#
  cb = ChessBoard(fen_position=sp)
  occ = cb.our_pieces | cb.enemy_pieces

  attack_squares = attack_tables.query_rook_attacks(0, occ)

  bin_idcs = BinaryHelper.create_bin_from_int_list([1, 2, 8, 16, 24, 32, 40, 48, 56])
  try:
    IS_EQ(attack_squares, bin_idcs)
  except:
    print('failed on test 1, output : {}, compare : {}'.format(attack_squares, bin_idcs))

  # ---#
  sp4 = 'rnbqkbnr/ppp1pp1p/6p1/3p4/1P6/8/PBPPPPPP/RN1QKBNR w KQkq - 0 3'
  cb = ChessBoard(fen_position=sp4)
  occ = cb.our_pieces | cb.enemy_pieces

  attack_squares4 = attack_tables.query_bishop_attacks(9, occ)
  b4 = BinaryHelper.create_bin_from_int_list([0, 16,2,18, 27, 36, 45, 54, 63])
  try:
    IS_EQ(attack_squares4, b4)
  except:
    print('failed on test 4, output : {}, compare : {}'.format(attack_squares4, b4))

  # ---#
  sp5= '7K/8/8/8/8/8/pp2B3/Qp6 w - - 0 1'
  cb = ChessBoard(fen_position=sp5)
  occ = cb.our_pieces | cb.enemy_pieces
  attack_squares4 = attack_tables.query_bishop_attacks(12, occ)
  b4 = BinaryHelper.create_bin_from_int_list([5,19,26,33,40,3,21,30,39])
  try:
    IS_EQ(attack_squares4, b4)
  except:
    print('failed on test 5, output : {}, compare : {}'.format(attack_squares4, b4))

  #---#
  sp = '2k5/8/3n4/8/8/8/8/B1K5 w - - 0 1'
  cb = ChessBoard(fen_position=sp)
  occ = cb.our_pieces | cb.enemy_pieces

  attack_squares = attack_tables.query_bishop_attacks(0, occ)

  bin_idcs = BinaryHelper.create_bin_from_int_list([9,18,27,36,45,54,63])
  try:
    IS_EQ(attack_squares, bin_idcs)
  except:
    print('failed on test 6, output : {}, compare : {}'.format(attack_squares, bin_idcs))





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

def run_hash_test(move_gen) :
  sp_orig = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  cb = ChessBoard(sp_orig)

  moves = move_gen.get_legal_moves(cb)

  print(cb.occ, cb.our_pieces_, cb.king_)

  cb.print_console(1)

  cb.update_from_move(moves[0])
  cb.mirror_side()

  cb.print_console(1)

  print(cb.occ, cb.our_pieces_, cb.king_)

  #
  # cb.set_zobrist()
  #
  # new_z = cb.get_zobrist()
  #
  # cb.mirror_side()
  #
  # cb.set_zobrist()
  #
  # new_after_set = cb.get_zobrist()
  #
  # #print(new_z, new_after_set)
  #
  # sp_mate_test = '8/1k1nn3/8/8/8/4B3/2K5/8 w - - 0 1'
  #
  # cb = ChessBoard(sp_mate_test)
  #






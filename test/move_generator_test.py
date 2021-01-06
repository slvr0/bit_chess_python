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

  sp4 = '1nbqkb1r/ppp1pppp/4n3/8/8/3N4/1PPPPPPP/R1BQ1K1R w KQk - 0 1'
  cb4 = ChessBoard(fen_position=sp4)

  cb4.mirror_side()

  #cb4.mirror_side()

  moves = move_gen.generate_legal_moves(cb4)

  cb4.print_console()

  moves.print(white_toact=False)



  # moves = move_gen.generate_legal_moves(cb4)
  #
  # #moves.print()
  #
  # m_idx = np.random.randint(0, len(moves))
  #
  # _00_idx = 0
  # _000_idx = 0
  #
  # for idx, m in enumerate(moves) :
  #   if m.spec_action == 'enp' : _00_idx = idx
  #
  # move = moves[2]
  # move.print()
  #
  # cb4.update_from_move(move)
  # cb4.print_console()
  #
  # print(cb4.enpassant_sq)






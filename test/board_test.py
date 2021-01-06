from core.chess_board import ChessBoard
from core.chess_square import Square

import numpy as np

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

def run_board_tests():

  #starting position , our pawns = 65280
  # our rooks = 129
  # our knights = 66

  starting_pos = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  chessboard = ChessBoard(fen_position=starting_pos)

  chessboard.get_pieces_idx('r')

  print_mode = 3
  spec_type = 'P'
  #chessboard.print_console(print_mode, spec_type)

  try :
    IS_EQ(chessboard.pieces['P'], 65280)
  except: print('failed on test 5, output : {}, compare : {}'.format(chessboard.pieces['P'], 65280))

  try:
    IS_EQ(chessboard.pieces['R'], 129)
  except: print('failed on test 6, output : {}, compare : {}'.format(chessboard.pieces['R'], 129))

  try:
    IS_EQ(chessboard.pieces['N'], 66)
  except : print('failed on test 7, output : {}, compare : {}'.format(chessboard.pieces['N'], 66))

  try :
    IS_EQ(chessboard.pieces['r'], 9295429630892703744)
  except : print('failed on test 8, output : {}, compare : {}'.format(chessboard.pieces['r'], 9295429630892703744))

  try :
    IS_EQ(chessboard.pieces['p'], np.uint64(0x00FF000000000000))
  except : print('failed on test 9, output : {}, compare : {}'.format(chessboard.pieces['p'], np.uint64(0x00FF000000000000)))


  chessboard_2 = 'rnbqkbnr/pp1p2pp/5p2/2p1P3/8/2N5/PPP1PPPP/R1BQKBNR w KQkq - 0 4'
  chessboard.reset_board()

  try :
    IS_EQ(chessboard.pieces['p'], np.uint64(0))
  except : print('failed on test 10, output : {}, compare : {}'.format(chessboard.pieces['p'], np.uint64(0)))

  chessboard.read_from_fen(chessboard_2)

  try :
    IS_EQ(chessboard.pieces['P'], np.uint64(68719539968))
  except : print('failed on test 11, output : {}, compare : {}'.format(chessboard.pieces['P'], np.uint64(68719539968)))

  sp1 = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  chessboard3 = ChessBoard(sp1)

  ind_all_white_pieces = chessboard3.get_all_pieces(ours=True)
  ind_all_black_pieces = chessboard3.get_all_pieces(ours=False)

  ind_white_list = chessboard3.get_pieces_idx_from_uint(ind_all_white_pieces)
  ind_black_list = chessboard3.get_pieces_idx_from_uint(ind_all_black_pieces)

  correct_white = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
  correct_black = [63,62,61,60,59,58,57,56,55,54,53,52,51,50,49,48]

  try :
    IS_EQUAL_LIST(ind_white_list, correct_white)
  except:
    print('failed on test 12, output : {}, compare : {}'.format(ind_white_list, correct_white))

  try:
    IS_EQUAL_LIST(ind_black_list, correct_black)
  except:
    print('failed on test 13, output : {}, compare : {}'.format(ind_black_list, correct_black))











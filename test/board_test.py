from chess_board import ChessBoard

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


def run_board_tests():

  #starting position , our pawns = 65280
  # our rooks = 129
  # our knights = 66

  starting_pos = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  chessboard = ChessBoard(fen_position=starting_pos)

  chessboard.get_pieces_idx('r')

  print_mode = 3
  spec_type = 'P'
  chessboard.print_console(print_mode, spec_type)

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










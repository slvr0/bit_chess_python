
from nn.data_parser import NN_DataParser

from core.chess_move import ChessMove, promo_types
from core.chess_board import ChessBoard

def run_nn_dp_test(nn_dp, move_gen) :

  #make 10 random moves
  #connect them to the parser output to see we get the correct nn output info

  m1 = ChessMove(8, 24, 'P') #26*8
  m2 = ChessMove(0, 24, 'R')
  m3 = ChessMove(0, 26, 'R') #illegal
  m4 = ChessMove(19, 37, 'b')
  m5 = ChessMove(27, 44, 'n')
  m6 = ChessMove(48, 56, 'P', '=' + promo_types[0])
  m7 = ChessMove(50, 58, 'P', '=' + promo_types[2])

  m1_idx = nn_dp.nn_move(m6)

  sp = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  cb = ChessBoard(sp)

  board_tensor = nn_dp.nn_board(cb)

  print(board_tensor)








### IMPORTANT
### The focus on this code is to use test cases to satisify that all logic is working correct!



# scrapboard structure
# board consist of a uint64_t for each piece type, the ones represent position of each piece
# ex. our_pawns, our_knights, our_bishops, our_rooks, our_queens, our_king
# and enemy_pawns, etc...

# board will have following functionality :
# debug, printout in console mod aswell as genering a fen string line,
# queering legal moves , returning a list of possible actions (not handling serialization of those, deal with it somewhere else)
# flipping the board , and thereby storing what side is currently acting on it (white/black = 1/0)

#well start with this, seems hard enough. queering legal moves is later prio ( we want attack tables generated first )

from chess_board import ChessBoard

from test.square_test import run_square_tests
from test.board_test import run_board_tests
if __name__ == '__main__':


    # example_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    # chessboard = ChessBoard(fen_position=example_fen)

    run_square_tests()
    run_board_tests()





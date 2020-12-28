

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

#future  :
#board serializer : takes in a chessboard and outputs 12 tensors (for each piece type )
#castling class, takes care of castling rights and check if possible in current state
#repetion class, checks 50 move rule, threefold repetition
#attack tables, caching all possible attacks with magic bitboard combinations
#boardplay wrapper, a class that wraps logic so user can simply play a game without touching logic
#for example, class with step taking a chess action input and outputs if game is over, next gameboard state and reward(reward is = 1 for winner etc.)
#network preparation, pytorch net with agent
#the memory and its algorithm, playing games will result in millions of positions, it will be too broad action space,
#have to be limited , learn about monte carlo search tree to optimize the training data

from chess_board import ChessBoard

from test.square_test import run_square_tests
from test.board_test import run_board_tests
from test.attack_tables_test import run_attack_tables_test
from test.move_generator_test import run_move_generator_test

if __name__ == '__main__':

    #run_square_tests()
    #run_board_tests()
    #run_attack_tables_test()
    run_move_generator_test()





#i want this file to execute all testcases that are in the directory, so it needs to look through files and
#manully execute them somehow

from test.square_test import run_square_tests
from test.board_test import run_board_tests
from test.attack_tables_test import run_attack_tables_test
from test.move_generator_test import run_move_generator_test

from core.move_generator import MoveGenerator
import test.random_chessplay_test

def _run_tests(move_gen) :
  #run_square_tests()
  #run_board_tests()
  #run_attack_tables_test(move_gen)
  run_move_generator_test(move_gen)
  #test.random_chessplay_test.run_test(move_gen)

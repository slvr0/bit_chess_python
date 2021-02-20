
#i want this file to execute all testcases that are in the directory, so it needs to look through files and
#manully execute them somehow

from test.square_test import run_square_tests
from test.board_test import run_board_tests
from test.attack_tables_test import run_attack_tables_test
from test.move_generator_test import run_move_generator_test

from core.move_generator import MoveGenerator
import test.random_chessplay_test
import test.hash_test
import test.nn_dataparse_test
import test.network_test
def _run_tests(nn_dp, move_gen) :
  #run_square_tests()
  #run_board_tests()
  #run_attack_tables_test(move_gen)
  run_move_generator_test(move_gen)
  #test.random_chessplay_test.run_test(move_gen)
  #test.hash_test.run_hash_test(move_gen)
  #test.nn_dataparse_test.run_nn_dp_test(nn_dp, move_gen)
  #test.network_test.run_network_test(nn_dp, move_gen)


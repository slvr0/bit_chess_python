
from wrappers.chess_env import ChessBoard,ChessEnvironment
from core.move_generator import MoveGenerator
import numpy as np

#this test just sets up a chess wrapper and plays the game using random moves
from copy import deepcopy
from time import time


def dummy_debug(white_toact, actions, random_move, cb_before, cb_after):
  print("Player: ", ['black', 'white'][white_toact])
  actions[random_move].print(white_toact)
  print("Board before move: ")
  cb_before.print_console()
  print("Board after move: ")
  cb_after.print_console()
  print("Our pieces :")
  cb_before.print_console(1)

def run_test(move_generator) :

  cb = ChessBoard()

  standard_position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

  chessboard = ChessBoard(standard_position)
  chess_environment = ChessEnvironment(move_generator, chessboard)

  max_moves = 100
  games     = 250
  found_endgame = False

  t0 = time()
  reset_time = 0
  step_time = 0
  getting_legal_action_time = 0
  getting_env_info = 0
  nr_moves_analyzed = 0

  for game in range(games) :
    t_r_0 = time()
    chess_environment.reset()
    reset_time += time() - t_r_0

    to_act = 1
    actions = []
    r_move = 0
    board = None
    cb_before = None
    cb_after = None

    for i in range(max_moves) :

      l_action_time = time()

      actions = chess_environment.get_legalmoves_inpos()
      # try :
      #
      # except :
      #   print("Failed to catch new moves")
      #   dummy_debug(to_act, actions, r_move, cb_before, cb_after)

      getting_legal_action_time += time() - l_action_time

      nr_moves_analyzed += len(actions)

      info_time = time()
      status, reward, white_toact, terminal, repeats = chess_environment.get_env_info()
      getting_env_info += time() - info_time

      if terminal :
        # print("Game over!", "result : ", status ,"actions available for current player:" , len(actions), "who acts? : ", ['black',
        #                              'white'][white_toact] ,  ', moves repeated : ', repeats)
        chess_environment.reset()
        break

      random_move = np.random.randint(len(actions))
      cb_before = deepcopy(chess_environment.cb)
      cb_after = deepcopy(chess_environment.explore(random_move))
      to_act = white_toact
      r_move = random_move

      time_stepping = time()
      chess_environment.step(random_move)
      step_time += time() - time_stepping


  print("total simul time : ", time() - t0, 'total time resetting: ',reset_time , ' time getting actions', getting_legal_action_time)
  print('getting env info', getting_env_info, 'stepping time' , step_time, "total moves found", nr_moves_analyzed)
  print("actions per second : " ,  int(nr_moves_analyzed / getting_legal_action_time))


  print("time info ", move_generator.dt0, move_generator.dt1, move_generator.dt2)


















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

  standard_position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

  cb0 = ChessBoard(standard_position)

  chess_environment = ChessEnvironment(move_generator)

  max_moves = 100
  games     = 5000

  t0 = time()
  reset_time = 0
  step_time = 0
  getting_legal_action_time = 0
  getting_env_info = 0
  nr_moves_analyzed = 0

  for game in range(games) :

    t_r_0 = time()
    reset_time += time() - t_r_0

    actions = []

    chess_environment.reset(cb0)

    for i in range(max_moves) :

      try :
        l_action_time = time()
        actions = chess_environment.get_legal_moves()
        getting_legal_action_time += time() - l_action_time

      except Exception as e:
        print(e)
        #dummy_debug(to_act, actions, r_move, cb_before, cb_after)

      nr_moves_analyzed += len(actions)

      info_time = time()
      status, reward, white_toact, terminal, repeats = chess_environment.get_board_info(actions)
      getting_env_info += time() - info_time

      if terminal :
        #cb.print_console()
        break

      random_move = np.random.randint(len(actions))

      time_stepping = time()
      chess_environment.step(actions, random_move)
      step_time += time() - time_stepping

    #actions[random_move].print()
    # print(i, status, reward, white_toact, terminal, repeats, len(actions))
    # cb.print_console()

  print("total simul time : ", time() - t0, 'total time resetting: ',reset_time , ' time getting actions', getting_legal_action_time)
  print('getting env info', getting_env_info, 'stepping time' , step_time, "total moves found", nr_moves_analyzed)
  print("actions per second : " ,  int(nr_moves_analyzed / getting_legal_action_time))


  #print("time info ", move_generator.dt0, move_generator.dt1, move_generator.dt2)

















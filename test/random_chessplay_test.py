
from wrappers.chess_env import ChessBoard,ChessEnvironment
from core.move_generator import MoveGenerator
import numpy as np

#this test just sets up a chess wrapper and plays the game using random moves
from copy import deepcopy
from time import time

def run_test() :

  testboard = ChessBoard()

  standard_position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
  move_generator = MoveGenerator()
  chessboard = ChessBoard(standard_position)
  chess_environment = ChessEnvironment(move_generator, chessboard)

  max_moves = 100
  games     = 100
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
    for i in range(max_moves) :

      l_action_time = time()
      actions = chess_environment.get_legalmoves_inpos()
      getting_legal_action_time += time() - l_action_time

      nr_moves_analyzed += len(actions)

      info_time = time()
      status, reward, white_toact, board_pos_value, terminal, repeats = chess_environment.get_env_info()
      getting_env_info += time() - info_time

      if terminal :
        # print("Game over!", "result : ", status ,"actions available for current player:" , len(actions), "who acts? : ", ['black',
        #                              'white'][white_toact] ,  ', moves repeated : ', repeats)

        break

      random_move = np.random.randint(len(actions))

      time_stepping = time()
      chess_environment.step(random_move)
      step_time += time() - time_stepping

  print("total simul time : ", time() - t0, 'total time resetting: ',reset_time , ' time getting actions', getting_legal_action_time)
  print('getting env info', getting_env_info, 'stepping time' , step_time, "total moves found", nr_moves_analyzed)
  print("actions per second : " ,  int(1 / (getting_legal_action_time / nr_moves_analyzed)))


















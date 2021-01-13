
#performs a rollout from node X and backpropagates visits and scores for the tree
import numpy as np

from copy import deepcopy, copy
from wrappers.chess_env import ChessEnvironment
from core.chess_board import ChessBoard
from core.chess_move import ChessMove

def dummy_debug(white_toact, actions, random_move, cb_before, cb_after):
  print("Player: ", ['black', 'white'][white_toact])
  actions[random_move].print(white_toact)
  print("Board before move: ")
  cb_before.print_console()
  print("Board after move: ")
  cb_after.print_console()
  print("Our pieces :")
  cb_before.print_console(1)

class MCTS_Rollout :
  def __init__(self) :
    pass

  def simulate_rollout(self, cb, env):
    np.random.seed(123)

    max_moves = 100
    move = 0
    terminal = False

    env.reset(cb)

    promo_has_happened = False
    castle_has_happened = False
    enp_has_happened = False

    movelist = []
    boardlist = []

    white_start =  -1 if not cb.white_to_act else 1

    while move < max_moves and not terminal :
      move += 1

      try :
        actions = env.get_legal_moves()
      except Exception as e :
        print(e)
        # for action, board in zip(movelist, boardlist) :
        #   action.print()
        #   board.print_console()
        #
        # print(castle_has_happened)
        # print(promo_has_happened)
        # print(enp_has_happened)
        exit()

      status, score, white_toact, done, repeats = env.get_board_info(actions)

      if done:
        return score, status

      n_actions = len(actions)
      action = np.random.randint(n_actions)

      #boardlist.append(env.get_state())
      #movelist.append(actions[action])

      if actions[action].spec_action == 'O-O' or actions[action].spec_action == 'O-O-O' :
        castle_has_happened = True
      elif actions[action].promotion != '' : promo_has_happened = True
      elif actions[action].spec_action == 'enp':
        enp_has_happened = True

      env.step(actions, action)

    return .5 * white_start , status

  def backward(self, mcts_node, score):
    mcts_node.backprop_score(score)





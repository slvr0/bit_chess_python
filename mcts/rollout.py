
#performs a rollout from node X and backpropagates visits and scores for the tree
import numpy as np

from copy import deepcopy
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
  def __init__(self, mcts_node, chess_env) :

    self.chess_env = chess_env
    self.mcts_node = mcts_node

  def simulate_rollout(self, mcts_node):

    nb = ChessBoard()
    nb = self.chess_env.reset_from(nb, mcts_node.cb)

    max_moves = 100
    move = 0

    terminal = False
    reward = 0
    last_action = ChessMove(-1,-1)

    while move < max_moves and not terminal :
      move += 1

      try :
        actions = self.chess_env.get_legal_moves(nb)

        status, score, white_toact, done, repeats = self.chess_env.get_board_info(nb, actions)
        terminal = done
        n_actions = len(actions)

        if done:
          return score, status

        action = np.random.randint(n_actions)

        board_before = deepcopy(nb)
        board = self.chess_env.explore(nb, actions, action)
        last_action = actions[action]

        if board.pieces['K'] == 0 or board.pieces['k'] == 0 :
          print("this is were we lost the king")
          print("arrived from this board : ")
          board_before.print_console()
          print("sanity, The Actual board being iterated(above is deepcopy)")
          nb.print_console()
          print("after move this happened")
          board.print_console()
          last_action.print()
          print("all actions in position ")
          actions.print()

        nb = self.chess_env.step(nb, actions, action)

      except Exception as e:
        print("index error in rollout phase")
        print(e)
        print("arrived from this board : ")
        board_before.print_console()
        print("after move this happened")
        board.print_console()
        last_action.print()

    return score, status

  def backward(self, mcts_node, score):
    mcts_node.backprop_score(score)





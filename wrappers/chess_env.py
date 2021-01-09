
#idea to wrap the chess logic in this environment. Similar to gym classes
#but structure should support the tree searches necessary for mctt

from core.chess_board import ChessBoard
from core.move_generator import MoveGenerator
from copy import deepcopy, copy

#detach completely from chessboard
class ChessEnvironment :
  def __init__(self, move_gen = MoveGenerator):

    self.move_gen = move_gen
    self.states   = ['ongoing', 'white_win', 'black_win', 'draw']

  def get_legal_moves(self, cb):
    return self.move_gen.generate_legal_moves(cb)

  def get_board_info(self, cb, actions) :

    status = self.states[0]
    reward = 0
    terminal = False
    repeats = cb._50_rulecount

    if cb._50_rulecount >= 50 :
      status = self.states[3]
      reward = 0.5
      terminal = True

    if len(actions) == 0 :
      status = self.states[2] if cb.white_to_act else self.states[1]
      reward = 1
      terminal = True

    to_act = True if cb.white_to_act else False

    return status, reward, to_act, terminal, repeats

  #this doesnt change the environment but gives info on how the environment would change if action was taken
  def explore(self, cb, actions, action) :
    n_actions = len(actions)
    if action < 0 or action > n_actions :
      print("action to explore is not in bound of available moves for position")

    new_cb = deepcopy(cb)

    new_cb.update_from_move(actions[action])
    #new_cb.mirror_side()

    return new_cb

  #this changes the environment with the action taken
  def step(self, cb, actions, action) :
    n_actions = len(actions)
    if action < 0 or action >= n_actions: print(
      "action to explore is not in bound of available moves for position")

    new_cb = deepcopy(cb)

    new_cb.update_from_move(actions[action])
    new_cb.mirror_side()

    return new_cb

  def reset_from(self, from_cb, to_cb) :
    from_cb.reset_from(to_cb)
    return from_cb





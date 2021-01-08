
#idea to wrap the chess logic in this environment. Similar to gym classes
#but structure should support the tree searches necessary for mctt

from core.chess_board import ChessBoard
from core.move_generator import MoveGenerator
from copy import deepcopy

class ChessEnvironment :
  def __init__(self, move_gen = MoveGenerator, _from = ChessBoard):
    self.move_gen = move_gen

    if _from is None :
      self.cb = ChessBoard('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1') #original starting position
    else :
      self.cb = _from

    self.root_cb = ChessBoard('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

    self.actions = []

    self.states = ['ongoing', 'white_win', 'black_win', 'draw']

  def get_legalmoves_inpos(self):
    self.actions = self.move_gen.generate_legal_moves(self.cb)
    return self.actions

  def get_env_info(self) :

    status = self.states[0]
    reward = 0
    terminal = False
    repeats = self.cb._50_rulecount

    if self.cb._50_rulecount >= 50 :
      status = self.states[3]
      reward = 0.5
      terminal = True

    if len(self.actions) == 0 :
      status = self.states[2] if self.cb.white_to_act else self.states[1]
      reward = 1
      terminal = True

    to_act = True if self.cb.white_to_act else False

    return status, reward, to_act, terminal, repeats

  #this doesnt change the environment but gives info on how the environment would change if action was taken
  def explore(self, action) :
    n_actions = len(self.actions)
    if action < 0 or action > n_actions :
      print("action to explore is not in bound of available moves for position")

    new_cb = deepcopy(self.cb)
    new_cb.update_from_move(self.actions[action])

    return new_cb

  #this changes the environment with the action taken
  def step(self, action) :
    n_actions = len(self.actions)
    if action < 0 or action >= n_actions: print(
      "action to explore is not in bound of available moves for position")

    self.cb.update_from_move(self.actions[action])

    self.cb.mirror_side()

  def reset(self) :
    self.cb.reset_from(self.root_cb)

  def reset_to(self, cb) :
    self.cb = cb
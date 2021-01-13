
#idea to wrap the chess logic in this environment. Similar to gym classes
#but structure should support the tree searches necessary for mctt

from core.chess_board import ChessBoard
from core.move_generator import MoveGenerator
from copy import deepcopy, copy
from collections import Counter

#detach completely from chessboard
class ChessEnvironment :
  def __init__(self, move_gen = MoveGenerator):

    self.move_gen = move_gen
    self.states   = ['ongoing', 'white_win', 'black_win', 'draw']

    self.visited_states = []
    self.visited_counter = Counter()

  def get_state(self):
    return deepcopy(self.cb)

  #might have a bug in the future , starting as black and comparing zobrist keys
  def reset(self, cb):
    self.visited_states = []
    self.cb = deepcopy(cb)
    self.cb.set_zobrist()
    self.visited_states.append(self.cb.get_zobrist())
    self.visited_counter = Counter()

    self.white_start =  -1 if not cb.white_to_act else 1

  def get_legal_moves(self):
    return self.move_gen.get_legal_moves(self.cb)

  def get_board_info(self, actions) :

    #nr repeats
    most_visited_state = self.visited_counter.most_common(1)
    if len(most_visited_state) != 0 :
      _3fold = most_visited_state[0][1]
    else :
      _3fold = 0

    if _3fold == 3 :
      print("three fold reset!")

    status = self.states[0]
    reward = 0
    terminal = False
    repeats = self.cb._50_rulecount

    if self.cb._50_rulecount >= 50 :
      status = self.states[3]
      reward = 0.5
      terminal = True

    elif len(actions) == 0 :
      status = self.states[2] if self.cb.white_to_act else self.states[1]
      reward = 1
      terminal = True

    elif not self.cb.has_mating_mat() :
      status = self.states[3]
      reward = 0.5
      terminal = True

    elif _3fold >= 3 :
      status = self.states[3]
      reward = 0.5
      terminal = True

    to_act = True if self.cb.white_to_act else False

    return status, reward * self.white_start, to_act, terminal, repeats

  #this doesnt change the environment but gives info on how the environment would change if action was taken
  def explore(self, actions, action) :
    n_actions = len(actions)
    if action < 0 or action > n_actions :
      print("action to explore is not in bound of available moves for position")

    new_cb = self.cb.copy()
    new_cb.update_from_move(actions[action])

    return new_cb

  #this changes the environment with the action taken
  def step(self, actions, action) :
    n_actions = len(actions)
    if action < 0 or action >= n_actions: print(
      "action to explore is not in bound of available moves for position")

    self.cb.update_from_move(actions[action])

    #im not sure how to mirror the z keys. instead i hash the board constantly from the eyes of white player
    if self.cb.white_to_act :
      self.cb.set_zobrist()
      self.cb.mirror_side()
      self.visited_counter[self.cb.get_zobrist()] += 1
    else :
      self.cb.mirror_side()
      self.cb.set_zobrist()
      self.visited_counter[self.cb.get_zobrist()] += 1

  def reset_from(self, from_cb) :
    self.reset(from_cb)






#a node contains tensor info, a chessboard, state evaluation from the mcts algorithm
#which will be a combination of network eval, position eval and nr traversed
#the tree will be traversed with the help of a wrapper that extracts information from the chessposition to the node

from copy import deepcopy
import math
import numpy as np

C_fact = 2
C_score_weight = 1

class MCTS_node :
  def __init__(self, depth , cb, from_action = None, score=0, terminal=False, cb_as_nn=None, parent = None):
    self.depth = depth

    self.cb = deepcopy(cb)
    self.terminal = terminal
    self.cb_as_nn = cb_as_nn

    self.parent = parent
    self.childs = [] #MCTS_nodes
    self.n_visits = 0
    self.total_score = score
    self.from_action = from_action

  def get_childs_eval_score(self):
    eval_scores = []
    for child in self.childs :
      eval_scores.append(child.get_eval_score())

    return eval_scores

  #later append res
  def cache_nn_res(self, res):
    if self.from_action is not None :
      res += self.from_action._str_dirty(self.cb.white_to_act)

    if self.parent is None : return res
    else : return self.parent.cache_nn_res(res)

  def get_eval_score(self):
    if self.n_visits == 0 : return 0

    return abs(self.total_score / self.n_visits)

  #traverse upwards to root and collects all moves
  def get_action_tree(self, _str):
    if self.from_action is not None:
      _str += self.from_action.print()
      print(self.depth)

    if self.parent is None: return

  def is_leaf(self):
    return len(self.childs) == 0

  def add_child(self, mcts_child_node):
    self.childs.append(mcts_child_node)

  def get_child_scores(self):
    if self.is_leaf() : return []

    scores = []

    for cidx, child in enumerate(self.childs) :
      score = child.get_score()
      scores.append(round(score, ndigits=4))

    return scores

  #this is how we internally rank the node based on both the total score and its visits
  def get_score(self):
    if self.parent is None :
      print("trying to calculate eval score on root, doesnt apply")
      return 0

    if self.n_visits == 0 or self.parent.n_visits == 0 :
      return math.inf
    else :
      #print( C_score_weight * (self.total_score / self.n_visits) , C_fact * np.sqrt(np.log(self.parent.n_visits) / self.n_visits))
      return abs( C_score_weight * (self.total_score / self.n_visits) + C_fact * np.sqrt(np.log(self.parent.n_visits) / self.n_visits))

  #spawns all branches from node, returns nr of branches
  def expand(self, chess_env):

    chess_env.reset(self.cb)

    actions = chess_env.get_legal_moves()

    if len(actions) == 0 :
      self.terminal = True
      return 0

    status, reward, to_act, terminal, repeats = chess_env.get_board_info(actions)

    for action in range(len(actions)):
      new_cb = chess_env.explore(actions, action)
      new_cb.mirror_side()

      node = MCTS_node(self.depth + 1, new_cb, actions[action], 0, terminal, parent=self)
      self.add_child(node)

    return len(self.childs)

  def rollout(self, chess_env, rollout):

    score, status = rollout.simulate_rollout(self.cb, chess_env)

    self.backprop_score(score)

  def traverse_to_leaf(self):

    if self.is_leaf() : return self

    c_scores = self.get_child_scores()
    c_argmax = np.argmax(c_scores)
    return self.childs[c_argmax].traverse_to_leaf()

  def get_parent(self):
    return self.parent

  def backprop_score(self, score_inc):

    self.n_visits += 1
    if self.parent is None : return

    old_score = self.get_score()

    self.total_score += score_inc

    new_score = self.get_score()

    self.parent.backprop_score(score_inc)

  def destroy_children(self):
    self.childs = []







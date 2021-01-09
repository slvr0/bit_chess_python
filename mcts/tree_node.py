
#a node contains tensor info, a chessboard, state evaluation from the mcts algorithm
#which will be a combination of network eval, position eval and nr traversed
#the tree will be traversed with the help of a wrapper that extracts information from the chessposition to the node

from copy import deepcopy
import math
import numpy as np

C_fact = 2

class MCTS_node :
  def __init__(self, depth , cb, from_action, score=0, terminal=False, cb_as_nn=None, parent = None):
    self.depth = depth

    self.cb = deepcopy(cb)
    self.terminal = terminal
    self.cb_as_nn = cb_as_nn

    self.parent = parent
    self.childs = [] #MCTS_nodes
    self.n_visits = 0
    self.total_score = score
    self.eval_score = 0
    self.from_action = from_action

  def get_childs_eval_score(self):
    eval_scores = []
    for child in self.childs :
      eval_scores.append(child.get_eval_score())

    return eval_scores

  def get_eval_score(self):
    if self.n_visits == 0 : return 0

    return self.total_score / self.n_visits

  #this recursively collects all moves in the node until terminal is found
  def get_action_chain(self):

    if self.is_leaf(): return

    #print("depth = ",self.depth, self.get_childs_eval_score())

    iters = 0
    found_leaf = True
    best_child = 0

    scores = self.get_childs_eval_score()
    while iters < len(self.childs) and found_leaf :
      best_child = np.argmax(scores)
      iters +=1
      found_leaf = self.childs[int(best_child)].is_leaf()
      scores[int(best_child)] = 0

    #print(best_child)
    # depth 1 is first move , depth 0 is just a starting position

    self.childs[int(best_child)].from_action.print(white_toact=True if self.depth % 2 == 0 else False)



    self.childs[int(best_child)].get_action_chain()

    # if self.depth != 0 :
    #   self.from_action.print()
    #
    # argmax_child = np.argmax(self.get_child_scores())
    #
    # self.childs[argmax_child].get_action_chain()


  def is_leaf(self):
    return len(self.childs) == 0

  def add_child(self, mcts_child_node):
    self.childs.append(mcts_child_node)

  def get_child_scores(self):
    if self.is_leaf() : return []

    scores = []

    for cidx, child in enumerate(self.childs) :
      score = child.get_score()
      scores.append(round(score, ndigits=2))

    return scores

  #this is how we internally rank the node based on both the total score and its visits
  def get_score(self):
    if self.parent is None :
      print("trying to calculate eval score on root, doesnt apply")
      return

    if self.n_visits == 0 or self.parent.n_visits == 0 :
      return math.inf
    else :
      return (self.total_score / self.n_visits) + C_fact * np.sqrt(np.log(self.parent.n_visits) / self.n_visits)

  def get_parent(self):
    return self.parent

  def backprop_score(self, score_inc):

    self.n_visits += 1
    self.total_score += score_inc

    if self.parent is None : return
    else : self.parent.backprop_score(score_inc)


    # if self.depth == 0 :
    #   self.total_score += score_inc
    #   self.n_visits += 1
    #   return
    #
    # print(self.parent.depth)
    #
    # self.total_score += score_inc
    # self.n_visits += 1
    #
    # self.parent.backprop_score(score_inc)

  def destroy_children(self):
    self.childs = []







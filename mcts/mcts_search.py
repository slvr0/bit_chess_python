

#this initiates the tree and starts building an observation space
from mcts.tree_node import MCTS_node
from wrappers.chess_env import ChessEnvironment
from copy import deepcopy
from time import time
import numpy as np

class MCTS_Search :
  def __init__(self, chess_env, root_node, rollout, max_depth = 5, max_entries = 50000):
    self.chess_env = chess_env
    self.root_node = root_node
    self.rollout = rollout
    self.max_depth = 200
    self.max_entries = max_entries

    self.nodes_at_depth = [0] * self.max_depth

  def print_action_chain(self):
    self.root_node.get_action_chain()

  def print_nodestruct(self):
    for depth,nnodes in enumerate(self.nodes_at_depth) :
      print("Depth : ", depth, " ...|... ", "Nodes", nnodes)
      if nnodes == 0 : break

  def traverse_top_scores(self, node, n, f_out):
    scores = node.get_childs_eval_score()

    n_top = np.argpartition(scores, -n)[-n:]

    for top_scorer in n_top :
      if node.childs[top_scorer].is_leaf() :
        action_chain = node.childs[top_scorer].cache_nn_res("")
        f_out.write(action_chain)
        f_out.write("\n")
      else :
        self.traverse_top_scores(node.childs[top_scorer], n, f_out)

  def new_search(self):
    self.nodes_at_depth[0] = 1
    total_entries = 20
    total_rollouts = 0

    f_out = open("mcts_out.txt", "w")

    while total_entries < self.max_entries :

      optimal_leaf_node = self.root_node.traverse_to_leaf()

      n_visits = optimal_leaf_node.n_visits

      total_rollouts += 1

      action_chain = optimal_leaf_node.cache_nn_res("")
      score = optimal_leaf_node.get_score()
      f_out.write(action_chain + "(score({:.2f}))".format(score))
      f_out.write("\n")

      if n_visits == 0 :
        optimal_leaf_node.rollout(self.chess_env, self.rollout)
      else:
        new_entries = optimal_leaf_node.expand(self.chess_env)
        self.nodes_at_depth[optimal_leaf_node.depth + 1] += new_entries
        total_entries += new_entries

        if optimal_leaf_node.is_leaf() : #means its terminal
          optimal_leaf_node.terminal = True
          continue

        optimal_leaf_node.childs[0].rollout(self.chess_env, self.rollout)

    n = 4

    #collect result

    f_out.write("\n")
    f_out.write("Appending top action lines in tree")
    f_out.write("\n")

    self.traverse_top_scores(self.root_node, n, f_out)

    print("Total rollouts : ",total_rollouts, "Entries : ", total_entries, "rollout % : ", int(100 * total_rollouts / total_entries) ,
          " Check file mcts_out.txt for output result")
    self.print_nodestruct()

    f_out.close()































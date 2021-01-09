

#this initiates the tree and starts building an observation space
from mcts.tree_node import MCTS_node
from wrappers.chess_env import ChessEnvironment
from copy import deepcopy

import numpy as np

def ndummydebug(white_toact, cb, from_action):
  print("Player: ", ['black', 'white'][white_toact])
  print("got here from action : ")
  from_action.print()

  print("Board before move: ")
  cb.print_console()
  print("Our pieces :")
  cb.print_console(1)

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

  def initialize(self):
    #start by simply expanding the root node to gain one depth options

    actions = self.chess_env.get_legal_moves(self.root_node.cb)
    self.nodes_at_depth[0] = 1

    for action in range(len(actions)) :
      new_cb = self.chess_env.explore(self.root_node.cb, actions, action)
      status, reward, to_act, terminal, repeats = self.chess_env.get_board_info(new_cb, actions)
      node = MCTS_node(1, deepcopy(new_cb), actions[action], reward, terminal, parent=self.root_node)
      self.root_node.add_child(node)
      self.nodes_at_depth[1] += 1

  def print_nodestruct(self):
    for depth,nnodes in enumerate(self.nodes_at_depth) :
      print("Depth : ", depth, " ...|... ", "Nodes", nnodes)
      if nnodes == 0 : break

  def search(self):

    self.nodes_at_depth[0] = 1

    total_entries = 20
    total_rollouts = 0

    current = self.root_node

    start_as_white = current.cb.white_to_act

    is_leaf = False
    terminal_node = False

    find_nonleaf_iters = 0
    endscore = 0

    while total_entries < self.max_entries :

      is_leaf = current.is_leaf()

      while not is_leaf :
        find_nonleaf_iters+=1
        #set it to the best scoring child
        child_scores = current.get_child_scores()

        m_idx = np.argmax(child_scores)
        current = current.childs[m_idx]

        is_leaf = current.is_leaf()

      n_visits = current.n_visits

      if n_visits == 0  :

        endscore, status = self.rollout.simulate_rollout(current)

        total_rollouts += 1
        self.rollout.backward(current, endscore)

        current = self.root_node
        current.cb = deepcopy(self.root_node.cb)

      else :
        new_depth = current.depth + 1

        try :
          actions = self.chess_env.get_legal_moves(current.cb)
        except Exception as e :
          print("index error in search expansion")
          print(e)
          print("arrived from this board : ")
          current.parent.cb.print_console()
          current.from_action.print()

        status, reward, to_act, terminal, repeats = self.chess_env.get_board_info(current.cb, actions)

        for action in range(len(actions)):
          total_entries += 1
          new_cb = self.chess_env.step(current.cb, actions, action)
          node = MCTS_node(new_depth, new_cb, actions[action], 0, terminal, parent=current)
          current.add_child(node)

          if new_depth >= self.max_depth  : break
          self.nodes_at_depth[new_depth] += 1

        if len(actions) == 0:
          break

        else :
          current = current.childs[0]

        total_rollouts += 1
        endscore, status = self.rollout.simulate_rollout(current)

        self.rollout.backward(current, endscore)

        current = self.root_node
        current.cb = deepcopy(self.root_node.cb)

        continue

    print("n iterations finding non leaf node : ", find_nonleaf_iters, "total rollouts : ", total_rollouts, "n entries : ", total_entries)
    self.print_nodestruct()

    #current = self.root_node
    #current.cb = deepcopy(self.root_node.cb)

    self.root_node.get_action_chain()



































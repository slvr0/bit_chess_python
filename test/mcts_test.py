
from mcts.mcts_search import MCTS_Search
from mcts.rollout import MCTS_Rollout
from mcts.tree_node import MCTS_node

from core.chess_board import ChessBoard
from wrappers.chess_env import ChessEnvironment

def run_mcts_test(move_gen) :
  cb            = ChessBoard('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

  chess_env     = ChessEnvironment(move_gen=move_gen)
  root_node     = MCTS_node(0, cb, 0)
  rollout       = MCTS_Rollout(root_node, chess_env)
  mcts_search   = MCTS_Search(chess_env, root_node, rollout)

  #mcts_search.initialize()
  mcts_search.search()




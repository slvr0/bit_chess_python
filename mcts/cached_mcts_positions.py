
from core.chess_board import ChessBoard

class CachedMCTSPositions :
  cached_positions = {}
  def __init__(self):
    pass

  #nn log pairs is nn idcs paired with logits value from queured mcts session
  def add_entry(self, key, nn_log_pairs = []):
    if not self.exist(key) :
      self.cached_positions[key] = nn_log_pairs

  def exist(self, key = " "):
    if type(key) == int :
      return self.cached_positions.__contains__(key)
    elif type(key) == str :
      key  = ChessBoard(key).get_zobrist()
      return self.cached_positions.__contains__(key)
    else :
      return None

  def get(self, key = " "):
    if self.exist(key) : return True, self.cached_positions[ChessBoard(key).get_zobrist()]
    else : return False, None





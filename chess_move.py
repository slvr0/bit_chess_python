
import numpy as np
class ChessMove :
  def __init__(self, _from, to, ptype = '', spec_action = ''):
    self._from = _from
    self.to = to
    self.ptype = ptype
    self.spec_action = spec_action
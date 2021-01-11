
import numpy as np
from core.utils import board_notations

promo_types = ['N', 'B', 'R', 'Q']

class ChessMove :
  def __init__(self, _from, to, ptype = '', spec_action = ''):
    self._from = _from
    self.to = to
    self.ptype = ptype
    self.spec_action = spec_action
    self.promotion = ''

  def print(self, white_toact=True):
    p_translation = {
      'P': 'Pawn',
      'N': 'Knight',
      'B': 'Bishop',
      'R': 'Rook',
      'Q': 'Queen',
      'K': 'King'
    }
    if not white_toact:
      bn = board_notations[::-1]
    else:
      bn = board_notations

    print('------------------------ Chessmoves in position ------------------------')
    print("Move : ", p_translation[self.ptype], " from : ", bn[self._from], " to : ",
          bn[self.to], " special info : ", self.spec_action)

  def _str(self, white_toact=True) :
    p_translation = {
      'P': 'Pawn',
      'N': 'Knight',
      'B': 'Bishop',
      'R': 'Rook',
      'Q': 'Queen',
      'K': 'King'
    }
    if not white_toact:
      bn = board_notations[::-1]
    else:
      bn = board_notations

    return "Move : " + p_translation[self.ptype] + " from : " + bn[self._from] + " to : " + \
           bn[self.to] + " special info : " + self.spec_action

class ChessMoveList :
  def __init__(self):
    self.moves = []

  def __len__(self):
    return len(self.moves)

  def __getitem__(self, item):
    return self.moves[item]

  def __iter__(self):
    for each in self.moves :
      yield each

  def add_move(self, move):
    if move.ptype == 'P' and move.to >= 55 and move.spec_action == '' :
      for i in range(4) : 
        promo_move = ChessMove(move._from, move.to, move.ptype, '=' + promo_types[i])
        promo_move.promotion = promo_types[i]
        self.moves.append(promo_move)

    else :
      self.moves.append(move)

  def print(self, white_toact=True) :
    p_translation = {
      'P': 'Pawn',
      'N': 'Knight',
      'B': 'Bishop',
      'R': 'Rook',
      'Q': 'Queen',
      'K': 'King'
    }
    if not white_toact :
      bn = board_notations[::-1]
    else :
      bn = board_notations

    for chessmove in self.moves :
      print('------------------------ Chessmoves in position ------------------------')
      print("Move : " , p_translation[chessmove.ptype], " from : ", bn[chessmove._from], " to : ",
            bn[chessmove.to], " special info : ", chessmove.spec_action)
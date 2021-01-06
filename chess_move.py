
import numpy as np
from utils import board_notations

class Promotion :
  def __init__(self, type):
    self.type = ['knight', 'bishop', 'rook', 'queen']
    assert type in self.type

class ChessMove :
  def __init__(self, _from, to, ptype = '', spec_action = ''):
    self._from = _from
    self.to = to
    self.ptype = ptype
    self.spec_action = spec_action
    self.promotion = None

  def add_promotion_info(self, type):
    self.promotion = Promotion(type)

  def print(self):
    p_translation = {
      'P': 'Pawn',
      'N': 'Knight',
      'B': 'Bishop',
      'R': 'Rook',
      'Q': 'Queen',
      'K': 'King'
    }
    print("Move : ", p_translation[self.ptype], " from : ", board_notations[self._from], " to : ",
        board_notations[self.to], " special info : ", self.spec_action)

class ChessMoveList :
  def __init__(self):
    self.moves = []

  def __len__(self):
    return len(self.moves)

  def __getitem__(self, item):
    return self.moves[item]

  def add_move(self, move):
    if move.ptype == 'P' and move.to >= 55 :
      for promo_type in ['knight', 'bishop', 'rook', 'queen'] : # i dont know how i want this
        promo_move = ChessMove(move._from, move.to, move.ptype, '=' + promo_type)
        promo_move.promotion = Promotion(promo_type)
        self.moves.append(promo_move)

    else :
      self.moves.append(move)

  def print(self, white_toact=True):
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
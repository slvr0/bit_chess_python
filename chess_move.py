
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

class ChessMoveList :
  def __init__(self):
    self.moves = []

  def add_move(self, move):
    if move.ptype == 'P' and move.to >= 55 :
      move.add_promotion_info(Promotion(type) for type in ['knight', 'bishop', 'rook', 'queen'])

    self.moves.append(move)

  def print(self):
    p_translation = {
      'P': 'Pawn',
      'N': 'Knight',
      'B': 'Bishop',
      'R': 'Rook',
      'Q': 'Queen',
      'K': 'King',
    }
    for chessmove in self.moves :
      print('------------------------ Chessmoves in position ------------------------')
      print("Move : " , p_translation[chessmove.ptype], " from : ", board_notations[chessmove._from], " to : ",
            board_notations[chessmove.to], " special info : ", chessmove.spec_action)
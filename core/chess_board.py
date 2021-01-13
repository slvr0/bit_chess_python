
# scrapboard structure
# board consist of a for each piece type, the ones represent position of each piece
# ex. our_pawns, our_knights, our_bishops, our_rooks, our_queens, our_king
# and enemy_pawns, etc...

# board will have following functionality :
# debug, printout in console mod aswell as genering a fen string line,
# queering legal moves , returning a list of possible actions (not handling serialization of those, deal with it somewhere else)
# flipping the board , and thereby storing what side is currently acting on it (white/black = 1/0)

#well start with this, seems hard enough. queering legal moves is later prio ( we want attack tables generated first )

import numpy as np
import re
from core.chess_castle import Castling
from core.utils import board_notations, flip_horizontal, flip_vertical
from core.chess_move import ChessMove
from core.chess_square import _idx_64

from core.utils import _np_one, _np_zero, _np_64, zobrish_prehash
from copy import copy
from time import time

#example fen
    #rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

from core.chess_square import Square
from copy import deepcopy

ptypelist = {'P':0,'N':1,'B':2,'R':3,'Q':4,'K':5,'p':6,'n':7,'b':8,'r':9,'q':10,'k':11}

class ChessBoard :

  #calling reset from doesn't reposition from fen string rather from the input chessboard pieces, which is much faster
  def reset_from(self, cb):

    self.our_pieces = cb.our_pieces
    self.enemy_pieces = cb.enemy_pieces

    self.white_to_act = cb.white_to_act
    self.enpassant_sq = cb.enpassant_sq
    self.move_count = cb.move_count
    self._50_rulecount = cb._50_rulecount

    self.castling = cb.castling
    self.fen = cb.fen

  def reset(self):

    _np_zero = np.uint64(0x0)

    self.white_to_act = True

    self.enpassant_sq = -1
    self.move_count = 0
    self._50_rulecount = 0

    self.castling.reset()

    self.pawns_ = _np_zero
    self.bishops_ = _np_zero
    self.knights_ = _np_zero
    self.rooks_ = _np_zero
    self.queens_ = _np_zero
    self.king_ = _np_zero

    self.enemy_pawns_ = _np_zero
    self.enemy_bishops_ = _np_zero
    self.enemy_knights_ = _np_zero
    self.enemy_rooks_ = _np_zero
    self.enemy_queens_ = _np_zero
    self.enemy_king_ = _np_zero

    self.our_pieces_ = self.pawns_ | self.knights_ | self.bishops_ | self.rooks_ | self.queens_ | self.king_
    self.enemy_pieces_ = self.enemy_pawns_ | self.enemy_knights_ | self.enemy_bishops_ | self.enemy_rooks_ | self.enemy_queens_ | self.enemy_king_
    self.occ = self.our_pieces_ | self.enemy_pieces_

    self.z_hash = 0

    if self.fen != "": self.read_from_fen(fen_position=self.fen)

  def as_nn_tensor(self):
    np_nn = np.zeros(shape=(13,64), dtype=np.int)

    np_nn[0, self.get_pieces_idx_from_uint(self.pawns_)] = 1
    np_nn[1, self.get_pieces_idx_from_uint(self.knights_)] = 1
    np_nn[2, self.get_pieces_idx_from_uint(self.bishops_)] = 1
    np_nn[3, self.get_pieces_idx_from_uint(self.rooks_)] = 1
    np_nn[4, self.get_pieces_idx_from_uint(self.queens_)] = 1
    np_nn[5, self.get_pieces_idx_from_uint(self.king_)] = 1
    np_nn[6, self.get_pieces_idx_from_uint(self.enemy_pawns_)] = 1
    np_nn[7, self.get_pieces_idx_from_uint(self.enemy_knights_)] = 1
    np_nn[8, self.get_pieces_idx_from_uint(self.enemy_bishops_)] = 1
    np_nn[9, self.get_pieces_idx_from_uint(self.enemy_rooks_)] = 1
    np_nn[10, self.get_pieces_idx_from_uint(self.enemy_queens_)] = 1
    np_nn[11, self.get_pieces_idx_from_uint(self.enemy_king_)] = 1

    np_nn[12, 0] = 1 if self.castling.we_00() else 0
    np_nn[12, 1] = 1 if self.castling.we_000() else 0
    np_nn[12, 2] = 1 if self.castling.enemy_00() else 0
    np_nn[12, 3] = 1 if self.castling.enemy_000() else 0
    np_nn[12, 4] = 1 if self.white_to_act else 0
    np_nn[12, 5] = 1 if self.enpassant_sq != -1 else 0

    return np_nn

  def set_zobrist(self):

    zv = np.uint64(0x0)
    for square in range(64) :
      occ_idx = self.occ_by(square)

      if occ_idx == -1 : continue

      if not self.white_to_act :
        zv ^= zobrish_prehash[63 - square, occ_idx]
      else :
        zv ^= zobrish_prehash[square, occ_idx]

    self.z_hash = zv

  @staticmethod
  def count_ones(xv):
    x = np.uint64(xv)
    x -= (x >> np.uint64(1)) & np.uint64(0x5555555555555555)
    x = (x & np.uint64(0x3333333333333333)) + ((x >> np.uint64(2)) & np.uint64(0x3333333333333333))
    x = (x + (x >> np.uint64(4))) & np.uint64(0x0F0F0F0F0F0F0F0F)
    return (x * np.uint64(0x0101010101010101)) >> np.uint64(56)

  def has_mating_mat(self):
    if self.rooks_ or self.pawns_ or self.queens_ : return True

    if self.count_ones(self.our_pieces_ | self.enemy_pieces_) < 4 :
      return False

    if self.knights_ | self.enemy_knights_ : return True

    lq_bishop = np.uint64(0x55AA55AA55AA55AA)
    dq_bishop = np.uint64(0xAA55AA55AA55AA55)

    lq_at = (self.bishops_ | self.enemy_bishops_) & lq_bishop
    dq_at = (self.bishops_ | self.enemy_bishops_) & dq_bishop

    return True if lq_at and dq_at else False
#
  def update_zobrist(self, move):
    _from = move._from
    to = move.to
    ptype = move.ptype
    spec_action = move.spec_action
    promo = move.promotion

    if promo == '' and spec_action == '' :

      self.z_hash ^= zobrish_prehash[_from, ptypelist[ptype]]
      self.z_hash ^= zobrish_prehash[to, ptypelist[ptype]]

      return

    elif promo != '' :
      zidx = ptypelist[promo]

      self.z_hash ^= zobrish_prehash[_from, ptypelist[ptype]]
      self.z_hash ^= zobrish_prehash[to, zidx]

      return

    elif spec_action == 'O-O' :
      #5,7 swap
      self.z_hash ^= zobrish_prehash[7, ptypelist['R']]
      self.z_hash ^= zobrish_prehash[4, ptypelist['K']]

      self.z_hash ^= zobrish_prehash[5, ptypelist['R']]
      self.z_hash ^= zobrish_prehash[6, ptypelist['K']]

      return

    elif spec_action == 'O-O-O':
      # 0,3 swap
      self.z_hash ^= zobrish_prehash[0, ptypelist['R']]
      self.z_hash ^= zobrish_prehash[4, ptypelist['K']]

      self.z_hash ^= zobrish_prehash[3, ptypelist['R']]
      self.z_hash ^= zobrish_prehash[2, ptypelist['K']]

      return

    elif spec_action == 'enp' :
      zidx = ptypelist[promo]
      self.z_hash ^= zobrish_prehash[_from, ptypelist[ptype]]

      to_occ = self.occ_by(to)
      if to_occ != -1: self.z_hash ^= zobrish_prehash[to, to_occ]

      self.z_hash ^= zobrish_prehash[to, ptypelist[ptype]]
      self.z_hash ^= zobrish_prehash[to-8, ptypelist[ptype]]

      return

  def get_zobrist(self):
    return self.z_hash

  def copy(self):
    ncb = ChessBoard()

    ncb.pawns_ = self.pawns_
    ncb.bishops_ = self.bishops_
    ncb.knights_ = self.knights_
    ncb.rooks_ = self.rooks_
    ncb.queens_ = self.queens_
    ncb.king_ = self.king_

    ncb.enemy_pawns_ = self.enemy_pawns_
    ncb.enemy_bishops_ = self.enemy_bishops_
    ncb.enemy_knights_ = self.enemy_knights_
    ncb.enemy_rooks_ = self.enemy_rooks_
    ncb.enemy_queens_ = self.enemy_queens_
    ncb.enemy_king_ = self.enemy_king_

    ncb.our_pieces_ = self.our_pieces_
    ncb.enemy_pieces_ = self.enemy_pieces_
    ncb.occ = self.occ

    ncb.white_to_act = self.white_to_act

    ncb.enpassant_sq = self.enpassant_sq
    ncb.move_count = self.move_count
    ncb._50_rulecount = self._50_rulecount

    ncb.castling = self.castling
    ncb.fen = self.fen

    return ncb

  def __init__(self, fen_position = "") :
    _np_zero = np.uint64(0x0)

    self.pawns_ = _np_zero
    self.bishops_= _np_zero
    self.knights_= _np_zero
    self.rooks_= _np_zero
    self.queens_= _np_zero
    self.king_= _np_zero

    self.enemy_pawns_= _np_zero
    self.enemy_bishops_= _np_zero
    self.enemy_knights_= _np_zero
    self.enemy_rooks_= _np_zero
    self.enemy_queens_= _np_zero
    self.enemy_king_= _np_zero

    #try this out, scrap the godamn dictionary
    self.our_pieces_ = np.uint64(self.pawns_ | self.knights_ | self.bishops_ | self.rooks_ | self.queens_ | self.king_)
    self.enemy_pieces_ = np.uint64(self.enemy_pawns_ | self.enemy_knights_ | self.enemy_bishops_ | self.enemy_rooks_ | self.enemy_queens_ | self.enemy_king_)
    self.occ = np.uint64(self.our_pieces_ | self.enemy_pieces_)

    self.white_to_act = True

    self.enpassant_sq = -1
    self.move_count = 0
    self._50_rulecount = 0

    self.castling = Castling()
    self.fen = fen_position
    
    if fen_position != "" : self.read_from_fen(fen_position=fen_position)

  def mirror_side(self):

    self.white_to_act = False if self.white_to_act else True

    pawns_ = flip_horizontal(flip_vertical(self.pawns_))
    knights_ = flip_horizontal(flip_vertical(self.knights_))
    bishops_ = flip_horizontal(flip_vertical(self.bishops_))
    rooks_ = flip_horizontal(flip_vertical(self.rooks_))
    queens_ = flip_horizontal(flip_vertical(self.queens_))
    king_ = flip_horizontal(flip_vertical(self.king_))

    enemy_pawns_ = flip_horizontal(flip_vertical(self.enemy_pawns_))
    enemy_knights_ = flip_horizontal(flip_vertical(self.enemy_knights_))
    enemy_bishops_ = flip_horizontal(flip_vertical(self.enemy_bishops_))
    enemy_rooks_ = flip_horizontal(flip_vertical(self.enemy_rooks_))
    enemy_queens_ = flip_horizontal(flip_vertical(self.enemy_queens_))
    enemy_king_ = flip_horizontal(flip_vertical(self.enemy_king_))

    self.pawns_ = np.uint64(enemy_pawns_)
    self.knights_ = np.uint64(enemy_knights_)
    self.bishops_ = np.uint64(enemy_bishops_)
    self.rooks_ = np.uint64(enemy_rooks_)
    self.queens_ = np.uint64(enemy_queens_)
    self.king_ = np.uint64(enemy_king_)

    self.enemy_pawns_ = np.uint64(pawns_)
    self.enemy_knights_ = np.uint64(knights_)
    self.enemy_bishops_ = np.uint64(bishops_)
    self.enemy_rooks_ = np.uint64(rooks_)
    self.enemy_queens_ = np.uint64(queens_)
    self.enemy_king_ = np.uint64(king_)

    self.our_pieces_ = np.uint64(self.pawns_ | self.knights_ | self.bishops_ | self.rooks_ | self.queens_ | self.king_)

    self.enemy_pieces_ = np.uint64(self.enemy_pawns_ | self.enemy_knights_ | self.enemy_bishops_ | self.enemy_rooks_ | self.enemy_queens_ | self.enemy_king_)

    self.occ = np.uint64(self.our_pieces_ | self.enemy_pieces_)

    self.castling.mirror()

    self.enpassant_sq = 63 - self.enpassant_sq if self.enpassant_sq != -1 else -1

  def read_from_fen(self, fen_position):
    #read entry , count slashes for line division. have a counter for what square we are
    #visiting

    #when we reach square 0 (we count backward in FEN)
    #all info should be split with spaces

    #1 . who's acting w(hite), b(lack)
    #2. Castling right (white short, white long, black short , black long )
    #3. enpassant square, if not available, will be a simple dash
    #4 zero move nr start
    #5 move count

    # example fen
    # rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

    slot_idx = 63 - 7
    str_iter = 0
    line_step_count = 0

    while(line_step_count < 8 and fen_position[str_iter] != ' ') :
      s = fen_position[str_iter]

      #if a number is in the fen string, it means we have N amount of void slots on the board consecutively,
      #so we simply move the iterator N steps and continue as usual
      if s.isnumeric() :
        s_as_value = int(s)
        slot_idx += s_as_value
        str_iter += 1
        continue

      elif s == '/' :
        slot_idx -= 16
        line_step_count += 1
        str_iter += 1
        continue

      #skipping linebreaks and empty void and cancelling at end information,
      #only thing going here is piece info

      self.add_piece(slot_idx, s)

      slot_idx += 1
      str_iter += 1
    #skip enpassant move count and castling for now actually. just fill in pieces

    rem_string = fen_position[str_iter : ]
    rem_string = rem_string.split(' ')[1:]

    self.white_to_act = True if rem_string[0] == 'w' else False
    castle_string = rem_string[1]

    self.castling.set_we_00(True if 'K' in castle_string else False)
    self.castling.set_we_000(True if 'Q' in castle_string else False)
    self.castling.set_enemy_00(True if 'k' in castle_string else False)
    self.castling.set_enemy_000(True if 'q' in castle_string else False)

    enp_sq = rem_string[2].upper()
    if enp_sq != '-':
      self.enpassant_sq = [index for index,_s in enumerate(board_notations) if enp_sq in _s][0]

    self.move_count = int(rem_string[4])
    self._50_rulecount = int(rem_string[3])

    self.our_pieces_ = self.pawns_ | self.knights_ | self.bishops_ | self.rooks_ | self.queens_ | self.king_
    self.enemy_pieces_ = self.enemy_pawns_ | self.enemy_knights_ | self.enemy_bishops_ | self.enemy_rooks_ | self.enemy_queens_ | self.enemy_king_
    self.occ = self.our_pieces_ | self.enemy_pieces_

  def reset_board(self) :
    for key in self.pieces : self.pieces[key] = _np_zero

    self.our_pieces = _np_zero
    self.enemy_pieces = _np_zero
    self.all_pieces = _np_zero

  #mainly for hash func
  def occ_by(self, at_idx):
    if self.occ & _idx_64[at_idx] == 0 : return -1

    if self.pawns_ & _idx_64[at_idx] : return 0
    elif self.enemy_pawns_ & _idx_64[at_idx]: return 6
    elif self.knights_ & _idx_64[at_idx] : return 1
    elif self.bishops_ & _idx_64[at_idx] : return 2
    elif self.rooks_ & _idx_64[at_idx] : return 3
    elif self.queens_ & _idx_64[at_idx] : return 4
    elif self.king_ & _idx_64[at_idx] : return 5
    elif self.enemy_knights_ & _idx_64[at_idx] : return 7
    elif self.enemy_bishops_ & _idx_64[at_idx] : return 8
    elif self.enemy_rooks_ & _idx_64[at_idx] : return 9
    elif self.enemy_queens_ & _idx_64[at_idx] : return 10
    elif self.enemy_king_ & _idx_64[at_idx] : return 11

  def add_piece(self, at_idx, ptype = '') :
    #assert ptype in self.pieces.keys()

    if ptype == 'P' : self.pawns_ |= _idx_64[at_idx]
    elif ptype == 'N': self.knights_ |= _idx_64[at_idx]
    elif ptype == 'B' : self.bishops_ |= _idx_64[at_idx]
    elif ptype == 'R' : self.rooks_ |= _idx_64[at_idx]
    elif ptype == 'Q' : self.queens_ |= _idx_64[at_idx]
    elif ptype == 'K' : self.king_ |= _idx_64[at_idx]
    elif ptype == 'p' : self.enemy_pawns_ |= _idx_64[at_idx]
    elif ptype == 'n' : self.enemy_knights_ |= _idx_64[at_idx]
    elif ptype == 'b' : self.enemy_bishops_ |= _idx_64[at_idx]
    elif ptype == 'r' : self.enemy_rooks_ |= _idx_64[at_idx]
    elif ptype == 'q' : self.enemy_queens_ |= _idx_64[at_idx]
    elif ptype == 'k' : self.enemy_king_ |= _idx_64[at_idx]

    if ptype.isupper() :
      self.our_pieces_ |= _idx_64[at_idx]
    else :
      self.enemy_pieces_ |= _idx_64[at_idx]

    self.occ |= _idx_64[at_idx]

  def remove_piece(self, at_idx):

    s_64_idx = ~_idx_64[at_idx]

    self.pawns_ &= s_64_idx
    self.bishops_ &= s_64_idx
    self.knights_ &= s_64_idx
    self.rooks_ &= s_64_idx
    self.queens_ &= s_64_idx
    self.king_ &= s_64_idx
    self.enemy_pawns_ &= s_64_idx
    self.enemy_bishops_ &= s_64_idx
    self.enemy_knights_ &= s_64_idx
    self.enemy_rooks_ &= s_64_idx
    self.enemy_queens_ &= s_64_idx
    self.enemy_king_ &= s_64_idx

    self.our_pieces_ &= s_64_idx
    self.enemy_pieces_ &= s_64_idx
    self.occ &= s_64_idx

  def update_from_move(self, move):

    _from = move._from
    to = move.to
    ptype = move.ptype

    spec_action = move.spec_action
    promotion = move.promotion

    #this is the special cases, so just deal with them right away
    if spec_action == 'enp' :
      self.add_piece(to, ptype)
      self.remove_piece(_from)
      self.remove_piece(to - 8)
      self._50_rulecount = 0

    elif spec_action == 'O-O':
      if self.white_to_act :
        king_on = 4
        rook_on = 7
        self.remove_piece(king_on)
        self.remove_piece(rook_on)
        self.add_piece(6, 'K')
        self.add_piece(5, 'R')
      else:
        king_on = 3
        rook_on = 0
        self.remove_piece(king_on)
        self.remove_piece(rook_on)
        self.add_piece(1, 'K')
        self.add_piece(2, 'R')

    elif spec_action == 'O-O-O':
      if self.white_to_act:
        king_on = 4
        rook_on = 0
        self.remove_piece(king_on)
        self.remove_piece(rook_on)
        self.add_piece(2, 'K')
        self.add_piece(3, 'R')
      else:
        king_on = 3
        rook_on = 7
        self.remove_piece(king_on)
        self.remove_piece(rook_on)
        self.add_piece(5, 'K')
        self.add_piece(4, 'R')


    elif promotion != '':
      self.remove_piece(to)
      self.remove_piece(_from)
      self.add_piece(to, promotion)

    else :
      #normale
      self.remove_piece(to)
      self.remove_piece(_from)
      self.add_piece(to, ptype)

    self.move_count += 1
    self._50_rulecount = self._50_rulecount + 1 if ptype != 'P' else 0

    self.enpassant_sq = -1
    if ptype == 'P' and _from >= 8 and _from < 16 :
      dm = to - _from
      if dm == 16 : self.enpassant_sq = to - 8

    self.castling.update_castlestatus(chessmove=move, side=1 if self.white_to_act else 0)

  @staticmethod
  def get_pieces_idx_from_uint(pieces_uint64, num_bits = 64):
    return [num_bits - idx - 1 for idx, c in enumerate(format(pieces_uint64, f'0{num_bits}b')) if c == '1']

  def get_pieces_idx(self, ptype = '', num_bits = 64):

    if   ptype == 'P' : pieces_uint64 = self.pawns_
    elif ptype == 'B' : pieces_uint64 = self.bishops_
    elif ptype == 'N' : pieces_uint64 = self.knights_
    elif ptype == 'R' : pieces_uint64 = self.rooks_
    elif ptype == 'Q' : pieces_uint64 = self.queens_
    elif ptype == 'K' : pieces_uint64 = self.king_
    elif ptype == 'p' : pieces_uint64 = self.enemy_pawns_
    elif ptype == 'b' : pieces_uint64 = self.enemy_bishops_
    elif ptype == 'n' : pieces_uint64 = self.enemy_knights_
    elif ptype == 'r' : pieces_uint64 = self.enemy_rooks_
    elif ptype == 'q' : pieces_uint64 = self.enemy_queens_
    elif ptype == 'k' : pieces_uint64 = self.enemy_king_
    else : return []

    return [num_bits - idx - 1 for idx, c in enumerate(format(pieces_uint64, f'0{num_bits}b')) if c == '1']

  def fill_printer(self, print_mode, spec_type =''):
    printer = np.chararray(shape=(64,))

    printer[:] = ','

    ind_fill = []
    if print_mode == 0 : ind_fill = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
    elif print_mode == 1 : ind_fill = ['P', 'N', 'B', 'R', 'Q', 'K']
    elif print_mode == 2 :  ind_fill = ['p', 'n', 'b', 'r', 'q', 'k']
    elif print_mode == 3 : ind_fill = [spec_type]

    for notation in ind_fill :
      printer[self.get_pieces_idx(notation)] = notation

    return printer

  #print_mode = 0 : all pieces, 1 = white pieces, 2 = black pieces, 3 = specific type
  def print_console(self, print_mode = 0, spec_type=''):

    printer = self.fill_printer(print_mode=print_mode, spec_type=spec_type)

    print('____A___B___C___D___E___F___G___H___')
    idx = 56
    print(int(idx/8) + 1, end='')
    while idx >= 0 :
      if (idx + 1) % 8 == 0 :
        print(' |', printer[idx].decode("utf-8"), '|')
        idx -= 15
        if int(idx / 8) + 1 > 0 :  print(int(idx / 8) + 1, end='')
      else:
        print(' |', printer[idx].decode("utf-8"), end='')
        idx += 1
    print('____A___B___C___D___E___F___G___H___')  


  def print_bitboard(self, bitboard):
    printer = np.chararray(shape=(64,))
    fill_bit_idx = self.get_pieces_idx_from_uint(bitboard)
    for i in range(64) :
      if i in fill_bit_idx : printer[i] = 'X'
      else : printer[i] =','

    print('____A___B___C___D___E___F___G___H___')
    idx = 56
    print(int(idx/8) + 1, end='')
    while idx >= 0 :
      if (idx + 1) % 8 == 0 :
        print(' |', printer[idx].decode("utf-8"), '|')
        idx -= 15
        if int(idx / 8) + 1 > 0 :  print(int(idx / 8) + 1, end='')
      else:
        print(' |', printer[idx].decode("utf-8"), end='')
        idx += 1
    print('____A___B___C___D___E___F___G___H___')


  def get_fen(self):
    #this should read the pieces and not just return the string
    return self.fen
  
  
  
  




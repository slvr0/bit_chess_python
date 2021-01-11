
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

from core.utils import _np_one, _np_zero, _np_64

from time import time

#example fen
    #rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

from core.chess_square import Square
from copy import deepcopy

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

    # try this out, scrap the godamn dictionary
    self.our_pieces_ = self.pawns_ | self.knights_ | self.bishops_ | self.rooks_ | self.queens_ | self.king_
    self.enemy_pieces_ = self.enemy_pawns_ | self.enemy_knights_ | self.enemy_bishops_ | self.enemy_rooks_ | self.enemy_queens_ | self.enemy_king_
    self.occ = self.our_pieces_ | self.enemy_pieces_

    if self.fen != "": self.read_from_fen(fen_position=self.fen)

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
    self.our_pieces_ = self.pawns_ | self.knights_ | self.bishops_ | self.rooks_ | self.queens_ | self.king_
    self.enemy_pieces_ = self.enemy_pawns_ | self.enemy_knights_ | self.enemy_bishops_ | self.enemy_rooks_ | self.enemy_queens_ | self.enemy_king_
    self.occ = self.our_pieces_ | self.enemy_pieces_  

    self.white_to_act = True

    self.enpassant_sq = -1
    self.move_count = 0
    self._50_rulecount = 0

    self.castling = Castling()
    self.fen = fen_position
    
    if fen_position != "" : self.read_from_fen(fen_position=fen_position)

  def mirror_side(self):

    self.white_to_act = False if self.white_to_act else True

    our_pawns = flip_horizontal(flip_vertical(self.pawns_))
    our_knights = flip_horizontal(flip_vertical(self.knights_))
    our_bishops = flip_horizontal(flip_vertical(self.bishops_))
    our_rooks = flip_horizontal(flip_vertical(self.rooks_))
    our_queens = flip_horizontal(flip_vertical(self.queens_))
    our_kings = flip_horizontal(flip_vertical(self.king_))

    enemy_pawns = flip_horizontal(flip_vertical(self.enemy_pawns_))
    enemy_knights = flip_horizontal(flip_vertical(self.enemy_knights_))
    enemy_bishops = flip_horizontal(flip_vertical(self.enemy_bishops_))
    enemy_rooks = flip_horizontal(flip_vertical(self.enemy_rooks_))
    enemy_queens = flip_horizontal(flip_vertical(self.enemy_queens_))
    enemy_kings = flip_horizontal(flip_vertical(self.enemy_king_))

    self.pawns_ = enemy_pawns
    self.knights_ = enemy_knights
    self.bishops_ = enemy_bishops
    self.rooks_ = enemy_rooks
    self.queens_ = enemy_queens
    self.king_ = enemy_kings

    self.enemy_pawns_ = our_pawns
    self.enemy_knights_ = our_knights
    self.enemy_bishops_ = our_bishops
    self.enemy_rooks_ = our_rooks
    self.enemy_queens_ = our_queens
    self.enemy_king_ = our_kings

    self.our_pieces = self.pawns_ | self.knights_ | self.bishops_ | self.rooks_ | self.queens_ | self.king_
    self.enemy_pieces = self.enemy_pawns_ | self.enemy_knights_ | self.enemy_bishops_ | self.enemy_rooks_ | self.enemy_queens_ | self.enemy_king_

    self.occ = self.our_pieces | self.enemy_pieces

    self.castling.mirror()

    self.enpassant_sq = 63 - self.enpassant_sq if self.enpassant_sq != -1 else -1

  def get_piece_at_square(self, square):
    for k in self.pieces :
      if self.pieces[k] & Square(square).as_uint64() != 0 : return k

  def get_board(self):
    return self.our_pieces_ | self.enemy_pieces_

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

      #print("at slot idx : {}, showing : {}".format(slot_idx,s))

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

  def square_occupied_by(self, square):
    for k in self.pieces :
      if self.pieces[k] & (np.uint64(1) << np.uint64(square)) != 0 : return k

    return ''

  def reset_board(self) :
    for key in self.pieces : self.pieces[key] = _np_zero

    self.our_pieces = _np_zero
    self.enemy_pieces = _np_zero
    self.all_pieces = _np_zero

  def add_piece(self, at_idx, ptype = '') :
    #assert ptype in self.pieces.keys()

    if ptype == 'P' : self.pawns_ |= _idx_64[at_idx]
    elif ptype == 'B' : self.bishops_ |= _idx_64[at_idx]
    elif ptype == 'N' : self.knights_ |= _idx_64[at_idx]
    elif ptype == 'R' : self.rooks_ |= _idx_64[at_idx]
    elif ptype == 'Q' : self.queens_ |= _idx_64[at_idx]
    elif ptype == 'K' : self.king_ |= _idx_64[at_idx]
    elif ptype == 'p' : self.enemy_pawns_ |= _idx_64[at_idx]
    elif ptype == 'b' : self.enemy_bishops_ |= _idx_64[at_idx]
    elif ptype == 'n' : self.enemy_knights_ |= _idx_64[at_idx]
    elif ptype == 'r' : self.enemy_rooks_ |= _idx_64[at_idx]
    elif ptype == 'q' : self.enemy_queens_ |= _idx_64[at_idx]
    elif ptype == 'k' : self.enemy_king_ |= _idx_64[at_idx]


    if ptype.isupper() :
      self.our_pieces_ |= _idx_64[at_idx]
    else :
      self.enemy_pieces_ |= _idx_64[at_idx]

  def remove_piece(self, at_idx):

    s_64_idx = _idx_64[at_idx]
    self.pawns_ &= ~s_64_idx
    self.bishops_ &= ~s_64_idx
    self.knights_ &= ~s_64_idx
    self.rooks_ &= ~s_64_idx
    self.queens_ &= ~s_64_idx
    self.king_ &= ~s_64_idx
    self.enemy_pawns_ &= ~s_64_idx
    self.enemy_bishops_ &= ~s_64_idx
    self.enemy_knights_ &= ~s_64_idx
    self.enemy_rooks_ &= ~s_64_idx
    self.enemy_queens_ &= ~s_64_idx
    self.enemy_king_ &= ~s_64_idx

    self.our_pieces_ &= ~s_64_idx
    self.enemy_pieces_ &= ~s_64_idx
    self.occ &= ~s_64_idx

    # occ_type = ''
    # sq_64 = _idx_64[at_idx]
    # sq_64_inv = ~sq_64
    #
    # for k in self.pieces :
    #   self.pieces[k] &= sq_64_inv
    #   if self.pieces[k] & sq_64 :
    #     occ_type = k
    #     break
    #
    # if occ_type.isupper() :
    #   self.our_pieces &= ~_idx_64[at_idx]
    # else :
    #   self.enemy_pieces &= ~_idx_64[at_idx]

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

    elif spec_action == 'O-O':
      self.add_piece(to, ptype)
      self.remove_piece(_from)

      self.add_piece(5, 'R')
      self.remove_piece(7)

    elif spec_action == 'O-O-O':
      self.add_piece(to, ptype)
      self.remove_piece(_from)

      self.add_piece(3, 'R')
      self.remove_piece(0)

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

    self.castling.update_castlestatus(chessmove=move)

  @staticmethod
  def get_pieces_idx_from_uint(pieces_uint64, num_bits = 64):

    return [num_bits - idx - 1 for idx, c in enumerate(format(pieces_uint64, f'0{num_bits}b')) if c == '1']

    # if pieces_uint64 == 0 : return []
    #
    # pieces_as_bin = bin(pieces_uint64)[::-1][:-2]
    #
    # return [idx.start() for idx in re.finditer('1', pieces_as_bin)]


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

  @staticmethod
  def print_bitboard(bitboard):
    cb_t = ChessBoard()

    fill_bit_idx = cb_t.get_pieces_idx_from_uint(bitboard)
    for a_idx in fill_bit_idx: cb_t.add_piece(a_idx, 'P')
    cb_t.print_console()

  def get_fen(self):
    #this should read the pieces and not just return the string
    return self.fen
  
  
  
  




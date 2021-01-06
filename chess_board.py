
# scrapboard structure
# board consist of a uint64_t for each piece type, the ones represent position of each piece
# ex. our_pawns, our_knights, our_bishops, our_rooks, our_queens, our_king
# and enemy_pawns, etc...

# board will have following functionality :
# debug, printout in console mod aswell as genering a fen string line,
# queering legal moves , returning a list of possible actions (not handling serialization of those, deal with it somewhere else)
# flipping the board , and thereby storing what side is currently acting on it (white/black = 1/0)

#well start with this, seems hard enough. queering legal moves is later prio ( we want attack tables generated first )

import numpy as np
import re
from chess_castle import Castling
from utils import board_notations
from chess_move import ChessMove

#example fen
    #rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1

from chess_square import Square

class ChessBoard :
  def __init__(self, fen_position = "") :

    self.pieces = {

    'P': np.uint64(0),
    'N': np.uint64(0),
    'B': np.uint64(0),
    'R': np.uint64(0),
    'Q': np.uint64(0),
    'K': np.uint64(0),

    'p' : np.uint64(0),
    'n' : np.uint64(0),
    'b' : np.uint64(0),
    'r' : np.uint64(0),
    'q' : np.uint64(0),
    'k' : np.uint64(0)
    }

    self.white_to_act = True

    self.enpassant_sq = -1
    self.move_count = 0
    self._50_rulecount = 0

    self.castling = Castling()
    self.fen = fen_position
    
    if fen_position != "" : self.read_from_fen(fen_position=fen_position)

  def get_piece_at_square(self, square):
    for k in self.pieces :
      if self.pieces[k] & Square(square).as_uint64() != 0 : return k

  def get_all_pieces(self, ours = True):
    pieces = np.uint64(0)

    if ours :
      pc_keys = ['P', 'N', 'B', 'R', 'Q', 'K']
    else :
      pc_keys = ['p', 'n', 'b', 'r', 'q', 'k']

    for k in pc_keys :
      pieces |= self.pieces[k]

    return pieces

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

      self.add_piece(Square(slot_idx), s)

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

  def square_occupied_by(self, square):
    for k in self.pieces :
      if self.pieces[k] & (np.uint64(1) << np.uint64(square)) != 0 : return k

    return ''

  def reset_board(self) :
    for key in self.pieces :
      self.pieces[key] = np.uint64(0)

  def add_piece(self, square, ptype = '') :
    assert ptype in self.pieces.keys()
    self.pieces[ptype] |= square.as_uint64()

  def remove_piece(self, square):
    for k in self.pieces :
      self.pieces[k] &= ~square.as_uint64()

  def update_from_move(self, move):
    _from = move._from
    to = move.to
    ptype = move.ptype
    spec_action = move.spec_action
    self.promotion = move.promotion

    #this is the special cases, so just deal with them right away
    if spec_action == 'enp' :
      self.add_piece(Square(to), ptype)
      self.remove_piece(Square(_from))
      self.remove_piece(Square(to - 8))

    elif spec_action == 'O-O':
      self.add_piece(Square(to), ptype)
      self.remove_piece(Square(_from))

      self.add_piece(Square(5), ptype)
      self.remove_piece(Square(7))

    elif spec_action == 'O-O-O':
      self.add_piece(Square(to), ptype)
      self.remove_piece(Square(_from))

      self.add_piece(Square(3), ptype)
      self.remove_piece(Square(0))

    elif self.promotion is not None:
      self.remove_piece(Square(to))
      promo_type = self.promotion.type
      self.remove_piece(Square(_from))
      self.add_piece(Square(to), promo_type)

    else :
      #normale
      self.remove_piece(Square(to))
      self.remove_piece(Square(_from))
      self.add_piece(Square(to), ptype)

    self.move_count += 1
    self._50_rulecount = self._50_rulecount + 1 if ptype != 'P' else 0

    self.enpassant_sq = -1
    if ptype == 'P' and _from >= 8 and _from < 16 :
      dm = to - _from
      if dm == 16 : self.enpassant_sq = to - 8

    self.castling.update_castlestatus(chessmove=move)




    #remove piece from square
    #add piece to new square

    # cover special s
    #castling action
    #enp action
    #promotion

    #update move count
    #update 50 move rule
    #update enp square

    #update fen
    #update castling
    pass

  @staticmethod
  def get_pieces_idx_from_uint(pieces_uint64):
    if pieces_uint64 == 0 : return []

    pieces_as_bin = bin(pieces_uint64)[::-1][:-2]

    return [idx.start() for idx in re.finditer('1', pieces_as_bin)]

  def get_pieces_idx(self, ptype = ''):
    assert ptype in self.pieces.keys()

    pieces_uint64 = self.pieces[ptype]

    pieces_as_bin = bin(pieces_uint64)[::-1][:-2]

    return [idx.start() for idx in re.finditer('1', pieces_as_bin)]

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
    for a_idx in fill_bit_idx: cb_t.add_piece(Square(a_idx), 'P')
    cb_t.print_console()

  def get_fen(self):
    #this should read the pieces and not just return the string
    return self.fen
  
  
  
  




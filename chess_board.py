
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

    self.white_castle_short  = True
    self.white_castle_long   = True
    self.black_castle_short  = True
    self.black_castle_long   = True

    if fen_position != "" : self.read_from_fen(fen_position=fen_position)

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
      str_iter +=1
    #skip enpassant move count and casting for now actually. just fill in pieces

  def reset_board(self) :
    for key in self.pieces :
      self.pieces[key] = np.uint64(0)

  def add_piece(self, square , ptype = '') :
    assert ptype in self.pieces.keys()
    self.pieces[ptype] |= square.as_uint64()

  def get_pieces_idx_from_uint(self, pieces_uint64):
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

  def move_piece(self, ptype, sq_from = Square, sq_to = Square):
    assert ptype in self.pieces.keys()

    #sanity check
    p_idxs = self.get_pieces_idx(ptype)

    occup = False
    for p_idx in p_idxs :
      if p_idx == sq_from.as_int() :
        occup = True

    if not occup :
      print("the square is not occupied by the ptype input, no action performed")
      return

    mfrom_mask = sq_from.as_uint64() ^ np.uint64(0xFFFFFFFFFFFFFFFF)
    mto_mask = sq_to.as_uint64() ^ np.uint64(0xFFFFFFFFFFFFFFFF)
    self.pieces[ptype] &= mfrom_mask #removes the piece from square

    #remove what was currently on that square! abit sloppy but we dont know what we write over, so we remove all entries possible there
    for k in self.pieces :
      self.pieces[k] &= mto_mask

    self.pieces[ptype] |= sq_to.as_uint64() #adds it to the new place


  def print_bitboard(self, bitboard):
    cb_t = ChessBoard()

    fill_bit_idx = cb_t.get_pieces_idx_from_uint(bitboard)
    for a_idx in fill_bit_idx: cb_t.add_piece(Square(a_idx), 'P')
    cb_t.print_console()

  def print_fen(self):
    pass




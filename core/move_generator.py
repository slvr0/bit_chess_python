from core.chess_square import *
from core.chess_board import ChessBoard
from core.utils import *
from core.chess_attack_tables import *
from core.chess_move import ChessMove, ChessMoveList
from core.chess_square import Square, _idx_64

#implementation will be influenced by
#https://peterellisjones.com/posts/generating-legal-chess-moves-efficiently/

from time import time
import numpy as np

from core.utils import _np_zero, _np_one , _np_64

#so much bad code here , many functions and code snippets repeating

class MoveGenerator :
  def __init__(self):
    self.sliding_attacktables = SlidingAttackTables()

    #trying to sort out overflow issue
    with warnings.catch_warnings():
      warnings.simplefilter('error')

    self.sliding_attacktables.init_sliding_attacks(rooks=True)
    self.sliding_attacktables.init_sliding_attacks(rooks=False)

    self.pawn_attacks = IndexedPawnAttacks()
    self.knight_attacks = IndexedKnightAttacks()

    self.cb = None

    self.dt0 = 0
    self.dt1 = 0
    self.dt2 = 0

  def get_kingmoves(self, square):
    moves = _np_zero

    r_s, c_s = idx_to_row_col(square)

    r_0 = r_s - 1
    c_0 = c_s - 1

    for i in range(0,3):
      r = r_0 + i
      for j in range(0,3):
        c = c_0 + j

        if r >= 0 and r < 8 and c >= 0 and c < 8 :
          moves |= _idx_64[row_col_to_idx(r,c)]

    return moves

  #start from king, send out rays in all directions
  #collects push,pin,capture and n_attacks
  def get_push_pin(self, king, our_pieces, enemy_pieces, enemy_bishops, enemy_rooks, enemy_queens):

    t0 = time()

    m_dirs = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    on_board = lambda row, col : row >= 0 and row < 8 and col >= 0 and col < 8

    np_zeromask = np.uint64(0x0)

    push_mask_full = np.uint64(0x0)
    push_mask_dir  = np.uint64(0x0)
    capture_mask = np.uint64(0x0)

    n_attackers = 0
    pins = []

    r_qs = enemy_queens|enemy_rooks
    b_qs = enemy_queens|enemy_bishops

    is_bishop_queen = lambda c_idx_64 : c_idx_64 & b_qs
    is_rook_queen = lambda c_idx_64 : c_idx_64 & r_qs

    for direction in m_dirs :
      validate_bishop_queens = direction[0] != 0 and direction[1] != 0

      row, col = idx_to_row_col(king)

      push_mask_full |= push_mask_dir
      push_mask_dir &= np_zeromask

      pin_at = -1
      found_pin = False

      while True :
        row += direction[1]
        col += direction[0]

        if not on_board(row, col) :
          push_mask_dir &= np_zeromask
          break

        s_id = row_col_to_idx(row, col)
        n_sq_64 = _idx_64[s_id]

        # we need to make sure we are pinned/attacked by correct piecetype
        if n_sq_64 & enemy_pieces :

          if validate_bishop_queens and is_bishop_queen(n_sq_64) :
            found_true = True
          elif not validate_bishop_queens and is_rook_queen(n_sq_64):
            found_true = True
          else : found_true = False

          if not found_true :
            push_mask_dir &= np_zeromask
            break

          if found_pin :
            push_mask_dir |= _idx_64[row_col_to_idx(row, col)]
            pins.append((pin_at, push_mask_dir))
            push_mask_dir &= np_zeromask
            break
          else :
            capture_mask |= n_sq_64
            n_attackers += 1
            break

        push_mask_dir |= _idx_64[row_col_to_idx(row, col)]

        if n_sq_64 & our_pieces :
          push_mask_dir &= np_zeromask
          if found_pin : break #means we encountered 2 of our own pieces on ray == no pin

          found_pin = True
          pin_at = s_id

    self.dt0 += time() - t0

    return n_attackers, push_mask_full, capture_mask, pins

  #new attempt at a faster move generator
  def get_legal_moves(self, cb):
    # go through all squares. check every piece alternative.
    # append enemy attack squares, attacksquares wo king, capture squares and push squares
    # as well as king info, under attack etc

    t0 = time()
    movelist = ChessMoveList()

    attack_mask = np.uint64(0x0) #all enemy attack squares
    attack_mask_noking = np.uint64(0x0) #all enemy attack squares where our king is removed

    our_pieces = cb.our_pieces_
    enemy_pieces = cb.enemy_pieces_
    occ = our_pieces | enemy_pieces
    king = cb.king_
    enemy_king = cb.enemy_king_
    king_idx = -1
    knight_capture_mask = np.uint64(0x0)

    n_pawn_attackers = 0

    self.dt0 += time() - t0

    found_king = False

    for square in cb.get_pieces_idx_from_uint(occ) :
      t2 = time ()
      idx_64 = _idx_64[square]

      if idx_64 & cb.king_ :
        found_king = True

        king_moves = self.get_kingmoves(square)
        king_idx = square
        n_attackers, push_mask, capture_mask, pins \
          = self.get_push_pin(square, our_pieces, enemy_pieces, cb.enemy_bishops_, cb.enemy_rooks_, cb.enemy_queens_)
        self.dt2 += time()-t2

      elif idx_64 & cb.pawns_ :
        t2 = time()
        self.append_pseudo_pawnmoves(cb, square, movelist)
        self.dt2 += time() - t2

      elif idx_64 & cb.knights_ :
        t2 = time()
        self.append_pseudomove_general(cb, square, movelist, 'N')
        self.dt2 += time() - t2

      elif idx_64 & cb.bishops_ :
        t2 = time()
        self.append_pseudomove_general(cb, square, movelist, 'B')
        self.dt2 += time() - t2

      elif idx_64 & cb.rooks_ :
        t2 = time()
        self.append_pseudomove_general(cb, square, movelist, 'R')
        self.dt2 += time() - t2

      elif idx_64 & cb.queens_ :
        t2 = time()
        self.append_pseudomove_general(cb, square, movelist, 'Q')
        self.dt2 += time() - t2

      elif idx_64 & cb.enemy_pawns_:
        t1 = time()
        attacks = self.pawn_attacks.pawn_attacks_rev[square]
        if attacks & king : n_pawn_attackers += 1
        attack_mask |= attacks
        attack_mask_noking |= attacks
        self.dt1 += time() - t1

      elif idx_64 & cb.enemy_knights_:
        t1 = time()
        attacks = self.knight_attacks[square]
        attack_mask |= attacks
        attack_mask_noking |= attacks
        self.dt1 += time() - t1

        if attacks & king :
          knight_capture_mask |= idx_64

      elif idx_64 & cb.enemy_bishops_:
        t1 = time()
        attacks = self.sliding_attacktables.query_bishop_attacks(square, occ)
        attacks_noking = self.sliding_attacktables.query_bishop_attacks(square, occ & king)
        attack_mask |= attacks
        attack_mask_noking |= attacks_noking
        self.dt1 += time() - t1

      elif idx_64 & cb.enemy_rooks_:
        t1 = time()
        attacks = self.sliding_attacktables.query_rook_attacks(square, occ)
        attacks_noking = self.sliding_attacktables.query_rook_attacks(square, occ & king)
        attack_mask |= attacks
        attack_mask_noking |= attacks_noking
        self.dt1 += time() - t1

      elif idx_64 & cb.enemy_queens_:
        t1 = time()
        attacks = self.sliding_attacktables.query_rook_attacks(square, occ)  | self.sliding_attacktables.query_bishop_attacks(square, occ)
        attacks_noking = self.sliding_attacktables.query_rook_attacks(square, occ & king) | self.sliding_attacktables.query_bishop_attacks(square, occ & king)
        attack_mask |= attacks
        attack_mask_noking |= attacks_noking
        self.dt1 += time() - t1

      elif idx_64 & cb.enemy_king_:
        t1 = time()
        attacks = self.get_kingmoves(square)
        attack_mask |= attacks
        attack_mask_noking |= attacks
        self.dt1 += time() - t1

    #if we don't acquire n_attackers and masks at this point, means we dont have a king and a serious bug in the algorithm somewhere
    #check legality of moves
    if not found_king  :
      raise Exception("Didn't find our king, chessboard(king) {}: ".format(king))

    n_attackers += n_pawn_attackers
    capture_mask |= knight_capture_mask

    #legal king moves
    king_moves &= ~our_pieces
    king_moves &= ~attack_mask_noking
    king_moves &= ~enemy_king
    # finally remove movement to protected enemy pieces
    king_moves &= ~(attack_mask_noking & enemy_pieces)

    k_move_idcs = cb.get_pieces_idx_from_uint(king_moves)

    legal_movelist = ChessMoveList()

    for k_move_idx in k_move_idcs: legal_movelist.add_move(ChessMove(king_idx, k_move_idx, ptype='K'))

    if n_attackers > 1 : return legal_movelist

    #add legal moves, special cases for pins and when king is in check
    for index, move in enumerate(movelist) :
      _from = move._from
      _to = move.to
      _to_64 = _idx_64[_to]

      is_pinned = False
      pinned_index = -1
      for index, pin in enumerate(pins):
        if _from == pin[0]:
          is_pinned = True
          pinned_index = index
          break

      if n_attackers == 1  and _to_64 & (push_mask | capture_mask) and not is_pinned:
        legal_movelist.add_move(move)
        continue

      elif is_pinned and _idx_64[_to] & pins[pinned_index][1]:
        legal_movelist.add_move(move)
        continue

      elif not is_pinned and n_attackers == 0 :
        legal_movelist.add_move(move)

    if n_attackers == 0 :
      w_csq_00_64 = _idx_64[5] | _idx_64[6]
      w_csq_000_64 = _idx_64[2] | _idx_64[3]

      b_csq_00_64 = _idx_64[1] | _idx_64[2]
      b_csq_000_64 = _idx_64[4] | _idx_64[5]

      # we're able to castle, there's nothing there and there's nothing attacking connected castle squares. its then legal

      if cb.white_to_act :
        if cb.castling.we_00():
          if (w_csq_00_64 | _idx_64[1]) & occ == 0 and w_csq_00_64 & attack_mask == 0: legal_movelist.add_move(
            ChessMove(4, 6, 'K', 'O-O'))
        if cb.castling.we_000():
          if w_csq_000_64 & occ == 0 and w_csq_000_64 & attack_mask == 0: legal_movelist.add_move(
            ChessMove(4, 2, 'K', 'O-O-O'))
      else :
        if cb.castling.we_00():
          if b_csq_00_64 & occ == 0 and b_csq_00_64 & attack_mask == 0: legal_movelist.add_move(
            ChessMove(3, 1, 'K', 'O-O'))
        if cb.castling.we_000():
          if (b_csq_000_64 | _idx_64[6]) & occ == 0 and b_csq_000_64 & attack_mask == 0: legal_movelist.add_move(
            ChessMove(3, 5, 'K', 'O-O-O'))

    return legal_movelist

  def append_pseudomove_general(self, cb, square, movelist, ptype=''):
    ptype = ptype

    if ptype == 'N' : atc_64 = self.knight_attacks[square] & ~(cb.our_pieces_ | cb.enemy_king_)
    elif ptype == 'B' : atc_64 = \
      self.sliding_attacktables.query_bishop_attacks(square, cb.our_pieces_ | cb.enemy_pieces_) \
      & ~(cb.our_pieces_ | cb.enemy_king_)
    elif ptype == 'R' : atc_64 = \
      self.sliding_attacktables.query_rook_attacks(square, cb.our_pieces_ | cb.enemy_pieces_) \
      & ~(cb.our_pieces_ | cb.enemy_king_)
    elif ptype == 'Q' :
      r = self.sliding_attacktables.query_rook_attacks(square, cb.our_pieces_ | cb.enemy_pieces_) \
                   & ~(cb.our_pieces_ | cb.enemy_king_)
      b = self.sliding_attacktables.query_bishop_attacks(square, cb.our_pieces_ | cb.enemy_pieces_) \
          & ~(cb.our_pieces_ | cb.enemy_king_)
      atc_64 = r | b

    else  : return

    atc_idcs = cb.get_pieces_idx_from_uint(atc_64)
    [movelist.add_move(ChessMove(_from=square, to=idx, ptype=ptype)) for idx in atc_idcs]

  def append_pseudo_pawnmoves(self, cb, square, movelist):
    one_move = 8
    two_move = 16
    ptype = 'P'
    enp_sq = cb.enpassant_sq

    p_atc_64 = self.pawn_attacks[square] & ~cb.enemy_king_
    p_sq_idcs = cb.get_pieces_idx_from_uint(p_atc_64)

    for a_sq in p_sq_idcs :
      if enp_sq == a_sq :
        if self.spec_enp_legalcheck(cb, a_sq):
            movelist.add_move(ChessMove(square, a_sq, ptype=ptype, spec_action='enp'))

      elif _idx_64[a_sq] & cb.enemy_pieces_ != 0 :
        movelist.add_move(ChessMove(square, a_sq, ptype=ptype))

    if _idx_64[square + one_move] & cb.occ == 0:
      movelist.add_move(ChessMove(square, square + one_move, ptype=ptype))

    if square >= 8 and square <= 15 :
      if _idx_64[square + two_move] & cb.occ == 0 and \
              _idx_64[square + one_move] & cb.occ == 0: movelist.add_move(
        ChessMove(square, square + two_move, ptype=ptype))

  #this function covers the tricky horizontal discover check from enp captures, example here
  #https://lichess.org/analysis/8/4p3/8/2KP3q/8/1k6/8/8_b_-_-_0_1#2
  def spec_enp_legalcheck(self, cb, capt_from):
    #check if rook/queen on rank
    row, col = idx_to_row_col(capt_from)

    full_row = np.uint8(0xFF)
    full_row_idx = np.uint64(full_row << (row - 1) * 8)

    enemy_queens = cb.enemy_queens_
    enemy_rooks  = cb.enemy_rooks_
    king = cb.king_

    if (king | (enemy_rooks | enemy_queens)) & full_row_idx == 0 : return True

    else :
      lost_piece_sq = cb.enpassant_sq - 8

      cap_64 = _idx_64[capt_from]
      cap_lost_64 = _idx_64[lost_piece_sq]

      #get all attacks rays without the enp pieces
      all_atc_idc = cb.get_pieces_idx_from_uint(enemy_rooks | enemy_queens)
      occ_no_enp_pieces = (cb.our_pieces_ | cb.enemy_pieces_) & ~(cap_64 | cap_lost_64)
      for a_idx in all_atc_idc :
        attacks = self.sliding_attacktables.query_rook_attacks(a_idx, occ_no_enp_pieces)
        if attacks & king : return False

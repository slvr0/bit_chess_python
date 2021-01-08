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

  def reset_board(self):
    self.cb = None

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

  #this function covers the tricky horizontal discover check from enp captures, example here
  #https://lichess.org/analysis/8/4p3/8/2KP3q/8/1k6/8/8_b_-_-_0_1#2
  def spec_enp_legalcheck(self, capt_from):
    #check if rook/queen on rank
    row, col = idx_to_row_col(capt_from)

    full_row = np.uint8(0xFF)
    full_row_idx = np.uint64(full_row << (row - 1) * 8)

    kings = self.cb.pieces['k']
    queens = self.cb.pieces['q']
    our_king = self.cb.pieces['K']

    if (kings | queens) & full_row_idx == 0 : return True
    else :
      lost_piece_sq = self.cb.enpassant_sq - 8

      cap_64 = _idx_64[capt_from]
      cap_lost_64 = _idx_64[lost_piece_sq]

      #get all attacks rays without the enp pieces
      all_atc_idc = self.cb.get_pieces_idx_from_uint(kings | queens)
      occ_no_enp_pieces = (self.cb.our_pieces | self.cb.enemy_pieces) & ~(cap_64 | cap_lost_64)
      for a_idx in all_atc_idc :
        attacks = self.sliding_attacktables.query_rook_attacks(a_idx, occ_no_enp_pieces)
        if attacks & our_king != 0 : return False

    #bug, what if enemy own piece cover rays
  def calc_pushmoves(self, our_pieces, enemy_pieces, ksq, attacker_sq, attacker_type):
    if attacker_type == 'r':
      m_dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
    elif attacker_type == 'b':
      m_dirs = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    elif attacker_type == 'q':
      m_dirs = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    else:
      return ()

    attack_mask = _np_zero

    pin_at = -1
    pin_attackray = _np_zero

    for mdir in m_dirs:
      row, col = idx_to_row_col(attacker_sq)

      found_ray = False
      found_pin = False

      no_pin = False #if block by own piece

      pin_attackray |= _idx_64[attacker_sq]

      while True :
        row += mdir[1]
        col += mdir[0]

        if row <  0 or row > 7 or col <  0 or col > 7  : break

        new_idx = row_col_to_idx(row, col)

        if new_idx == ksq:
          found_ray = True
          break

        n_sq_64 = _idx_64[new_idx]

        if n_sq_64 & enemy_pieces != 0 : no_pin = True

        if our_pieces & n_sq_64 != 0 and not found_pin and not no_pin :
          found_pin = True
          pin_at = new_idx

        attack_mask |= n_sq_64
        pin_attackray |= n_sq_64

      if found_ray:
        break
      else:
        attack_mask = _np_zero
        pin_at = -1
        pin_attackray = _np_zero

    return attack_mask, (pin_at, pin_attackray)

  def get_enemy_attackinfo(self, cb ):
    king_pos = cb.pieces['K']

    king_idx = cb.get_pieces_idx_from_uint(king_pos)[0]

    enemy_pawns = cb.pieces['p']
    enemy_knights = cb.pieces['n']
    enemy_bishops = cb.pieces['b']
    enemy_queens = cb.pieces['q']
    enemy_rooks = cb.pieces['r']

    enemy_king_pos = cb.pieces['k']

    enemy_king_idx = cb.get_pieces_idx_from_uint(enemy_king_pos)[0]

    our_pieces = cb.our_pieces
    enemy_pieces = cb.enemy_pieces

    occ = our_pieces | enemy_pieces
    occ_no_king = occ - king_pos

    n_checkers = 0
    attacking_mask = _np_zero # all enemy attack squares, covering castle and similar
    attacking_mask_noking = _np_zero # same but with no king, need this to calculate correct king moves out of check

    push_mask = _np_zero #attack squares between slider and king
    capture_mask = _np_zero #attack squares where
    pins = [] #attack squares where pieces cannot move, now a tuple (at, from)

    enemy_king_moves = self.get_kingmoves(enemy_king_idx) & ~occ

    attacking_mask |= enemy_king_moves
    attacking_mask_noking |= enemy_king_moves

    knight_attacking_king = False

    #pawns
    p_idcs = cb.get_pieces_idx_from_uint(enemy_pawns)
    for p_idx in p_idcs :
      attacks = self.pawn_attacks.pawn_attacks_rev[p_idx]
      attacking_mask |= attacks
      attacking_mask_noking |= attacks
      if attacks & king_pos != 0:
        n_checkers += 1
        capture_mask |= _np_one << np.uint64(p_idx)

    #knights
    kn_idcs = cb.get_pieces_idx_from_uint(enemy_knights)
    for kn_idx in kn_idcs :
      attacks = self.knight_attacks[kn_idx]
      attacking_mask |= attacks
      attacking_mask_noking |= attacks
      if attacks & king_pos != 0 :
        n_checkers += 1
        knight_attacking_king = True
        capture_mask |= _np_one << np.uint64(kn_idx)

    #bishops
    b_idcs = cb.get_pieces_idx_from_uint(enemy_bishops)
    for b_idx in b_idcs:
      attacks = self.sliding_attacktables.query_bishop_attacks(b_idx, occ)
      attacks_noking = self.sliding_attacktables.query_bishop_attacks(b_idx, occ_no_king)
      attacking_mask |= attacks
      attacking_mask_noking |= attacks_noking

      if self.sliding_attacktables.query_bishop_attacks(b_idx, _np_zero) & king_pos != 0 :
        push, pin = self.calc_pushmoves(our_pieces, enemy_pieces, king_idx, b_idx, 'b')  # where we can block
        pins.append(pin)
        if attacks & king_pos != 0:
          n_checkers += 1
          push_mask |= push
          capture_mask |= _np_one << np.uint64(b_idx)

    #rooks
    r_idcs = cb.get_pieces_idx_from_uint(enemy_rooks)
    for r_idx in r_idcs:
      attacks = self.sliding_attacktables.query_rook_attacks(r_idx, occ)
      attacks_noking = self.sliding_attacktables.query_rook_attacks(r_idx, occ_no_king)
      attacking_mask |= attacks
      attacking_mask_noking |= attacks_noking

      if self.sliding_attacktables.query_rook_attacks(r_idx, _np_zero) & king_pos != 0:
        push, pin = self.calc_pushmoves(our_pieces, enemy_pieces, king_idx, r_idx, 'r')  # where we can block
        pins.append(pin)
        if attacks & king_pos != 0:
          n_checkers += 1
          push_mask |= push
          capture_mask |= _np_one << np.uint64(r_idx)

    #queens
    q_idcs = cb.get_pieces_idx_from_uint(enemy_queens)
    for q_idx in q_idcs:
      attacks = self.sliding_attacktables.query_rook_attacks(q_idx, occ)
      attacks |= self.sliding_attacktables.query_bishop_attacks(q_idx, occ)

      attacks_noking = self.sliding_attacktables.query_rook_attacks(q_idx, occ_no_king)
      attacks_noking |= self.sliding_attacktables.query_bishop_attacks(q_idx, occ_no_king)

      attacking_mask |= attacks
      attacking_mask_noking |= attacks_noking

      if (self.sliding_attacktables.query_bishop_attacks(q_idx, _np_zero) & king_pos != 0) or \
         (self.sliding_attacktables.query_rook_attacks(q_idx, _np_zero) & king_pos != 0) :
        push, pin = self.calc_pushmoves(our_pieces, enemy_pieces, king_idx, q_idx, 'q')  # where we can block
        pins.append(pin)
        if attacks & king_pos != 0:
          n_checkers += 1
          push_mask |= push
          capture_mask |= _np_one << np.uint64(q_idx)

    if knight_attacking_king :
      push_mask = _np_zero

    return {
    'n_checkers' : n_checkers,
    'attack_mask' : attacking_mask,
    'attack_mask_noking' :attacking_mask_noking,
    'push_mask' : push_mask,
    'capture_mask': capture_mask,
    'pins' : pins
    }

  def generate_legal_moves(self, cb):

    if self.cb is not None :
      self.reset_board()

    self.cb = cb
    self.our_pieces = self.cb.our_pieces
    self.enemy_pieces = self.cb.enemy_pieces

    all_moves = ChessMoveList()

    t0 = time()

    attackinfo = self.get_enemy_attackinfo(cb)

    self.n_checkers = attackinfo['n_checkers']
    self.attack_mask = attackinfo['attack_mask']
    self.attack_mask_noking = attackinfo['attack_mask_noking']
    self.push_mask = attackinfo['push_mask']
    self.capture_mask = attackinfo['capture_mask']
    self.pins = attackinfo['pins']

    self.our_pieces = cb.our_pieces
    self.enemy_pieces = cb.enemy_pieces
    self.occ = self.our_pieces | self.enemy_pieces

    self.king_square = cb.get_pieces_idx('K')[0]
    self.enemy_king_64 = cb.pieces['k']
    king_moves = self.get_kingmoves(self.king_square)

    t1 = time()

    #bug, the king can capture anywhere on the board if he's under check
    legal_king_moves = king_moves & (~self.attack_mask_noking & ~self.our_pieces & (~self.enemy_pieces & ~self.attack_mask))

    m_idc = cb.get_pieces_idx_from_uint(legal_king_moves)

    for k_move_idx in m_idc: all_moves.add_move(ChessMove(self.king_square, k_move_idx, ptype='K'))

    if self.n_checkers >= 2 :
      return all_moves #there's no other options

    self.king_in_check = True if self.n_checkers >= 1 else False

    t2 = time()

    p_idcs = cb.get_pieces_idx('P')
    self.append_pawnmoves(all_moves, p_idcs)

    kn_idcs = cb.get_pieces_idx('N')
    self.append_knightmoves(all_moves, kn_idcs)

    b_idcs = cb.get_pieces_idx('B')
    self.append_slidermoves(chessmove_list=all_moves, piece_idcs=b_idcs, pt='B')

    r_idcs = cb.get_pieces_idx('R')
    self.append_slidermoves(chessmove_list=all_moves, piece_idcs=r_idcs, pt='R')

    q_idcs = cb.get_pieces_idx('Q')
    self.append_slidermoves(chessmove_list=all_moves, piece_idcs=q_idcs, pt='Q')

    #castle moves
    if not self.king_in_check :

      csq_00_64  = _idx_64[5] | _idx_64[6]
      csq_000_64 = _idx_64[2] | _idx_64[3]

      #we're able to castle, there's nothing there and there's nothing attacking connected castle squares. its then legal
      if cb.castling.we_00() :
        if csq_00_64 & self.occ == 0 and csq_00_64 &  self.attack_mask  == 0 : all_moves.add_move(ChessMove(4, 6, 'K', 'O-O'))
      if cb.castling.we_000() :
        if csq_000_64 & self.occ == 0 and csq_000_64 & self.attack_mask == 0 : all_moves.add_move(ChessMove(4, 2, 'K', 'O-O-O'))

    t3 = time()

    self.dt0 += t1 - t0
    self.dt1 += t2 - t1
    self.dt2 += t3 - t2

    return all_moves

  def get_slider_attacks(self, s_idx, ptype):
    if ptype == 'Q' :
      return self.sliding_attacktables.query_rook_attacks(s_idx, self.occ) | self.sliding_attacktables.query_bishop_attacks(s_idx, self.occ)
    elif ptype == 'R' :
      return self.sliding_attacktables.query_rook_attacks(s_idx, self.occ)
    elif ptype == 'B' :
      return self.sliding_attacktables.query_bishop_attacks(s_idx, self.occ)
    else : return 0

  def append_slidermoves(self, chessmove_list, piece_idcs, pt):
    ptype = pt

    for idx in piece_idcs :
      idx_64 = _idx_64[idx]

      attacks = self.get_slider_attacks(idx, ptype) & ~(self.our_pieces | self.enemy_king_64)

      is_pinned = False

      if self.king_in_check :
        for pin in self.pins:
          if _idx_64[pin[0]] & idx_64 != 0:
            is_pinned = True

        if is_pinned : continue

        if self.capture_mask != 0 and attacks & self.capture_mask != 0: add_capture_mask = True
        else : add_capture_mask = False

        attacks &= self.push_mask

        if add_capture_mask : attacks |= self.capture_mask

        #there's probably a faster way for this method, check lc0
        attack_idcs = self.cb.get_pieces_idx_from_uint(attacks)
        [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

      else :
        pin_index  = -1

        for index, pin in enumerate(self.pins):
          if _idx_64[pin[0]] & idx_64 != 0:
            pin_index = index
            is_pinned = True
            break

        if is_pinned :
          _,_from_ray = self.pins[pin_index]
          attacks &= _from_ray

        attack_idcs = self.cb.get_pieces_idx_from_uint(attacks)
        [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

  def append_knightmoves(self,chessmove_list, kn_idcs):
    ptype = 'N'

    for idx in kn_idcs :
      is_pinned = False

      idx_64 = _np_one << np.uint64(idx)

      for pin in self.pins:
        if (_np_one << np.uint64(pin[0])) & idx_64 != 0:
          is_pinned = True

      if is_pinned : continue

      attacks = self.knight_attacks[idx] &  ~(self.our_pieces | self.enemy_king_64)

      if self.king_in_check :
        attacks = (self.push_mask & attacks) | (self.capture_mask & attacks)


      attack_idcs = self.cb.get_pieces_idx_from_uint(attacks)
      [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

  def append_pawnmoves(self, chessmove_list, p_idcs):
      one_move = 8
      two_move = 16

      enp_sq = self.cb.enpassant_sq

      ptype = 'P'

      for idx in p_idcs:
        idx_64 = _idx_64[idx]

        n_sq_onemove = _np_zero if idx + 8 >= 64 else _idx_64[idx + 8]
        n_sq_twomove = _np_zero if idx + 16 >= 64 else _idx_64[idx + 16]

        is_pinned = False

        if self.king_in_check :
          for pin in self.pins :
            if _idx_64[pin[0]] & idx_64 != 0 :
              is_pinned = True

          if is_pinned : continue

          if n_sq_onemove & self.push_mask != 0 :

            chessmove_list.add_move(ChessMove(idx, idx + one_move, ptype=ptype))
          if n_sq_twomove & self.push_mask != 0 :
            if idx <= 15:
              if n_sq_twomove & self.occ == 0 and \
                     n_sq_onemove & self.occ == 0:
                chessmove_list.add_move(ChessMove(idx, idx + two_move, ptype=ptype))

          attack_64 = self.pawn_attacks[idx]
          a_sq_idx = self.cb.get_pieces_idx_from_uint(attack_64)
          for a_sq in a_sq_idx :
            if enp_sq == a_sq :
              chessmove_list.add_move(ChessMove(idx, a_sq, ptype=ptype, spec_action='enp'))

            elif _idx_64[a_sq] & self.capture_mask != 0 :
              chessmove_list.add_move(ChessMove(idx, a_sq, ptype=ptype))

          continue #dont add normal moves

        pin_index  = -1

        for index, pin in enumerate(self.pins):
          if _idx_64[pin[0]] & idx_64 != 0:
            pin_index = index
            is_pinned = True
            break

        attack_64 = self.pawn_attacks[idx] & ~self.enemy_king_64

        if is_pinned :
          _, _from_ray = self.pins[pin_index]
          attack_64 &= _from_ray

        a_sq_idx = self.cb.get_pieces_idx_from_uint(attack_64)

        for a_sq in a_sq_idx:
          if enp_sq == a_sq:
            if self.spec_enp_legalcheck(a_sq) :
              chessmove_list.add_move(ChessMove(idx, a_sq, ptype=ptype, spec_action='enp'))

          if _idx_64[a_sq] & self.enemy_pieces != 0:
            chessmove_list.add_move(ChessMove(idx, a_sq, ptype=ptype))

        if is_pinned : continue

        # add all one moves
        if n_sq_onemove & self.occ == 0:
          chessmove_list.add_move(ChessMove(idx, idx + one_move, ptype=ptype))

        # add all two moves
        if idx <= 15 :
          if n_sq_twomove & self.occ == 0 and \
                  n_sq_onemove & self.occ == 0: chessmove_list.add_move(
            ChessMove(idx, idx + two_move, ptype=ptype))

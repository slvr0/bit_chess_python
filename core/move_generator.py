from core.chess_square import *
from core.chess_board import ChessBoard
from core.utils import *
from core.chess_attack_tables import *
from core.chess_move import ChessMove, ChessMoveList

#implementation will be influenced by
#https://peterellisjones.com/posts/generating-legal-chess-moves-efficiently/

from time import time

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

  def get_kingmoves(self, square):
    moves = np.uint64(0)

    r_s, c_s = idx_to_row_col(square)

    r_0 = r_s - 1
    c_0 = c_s - 1

    for i in range(0,3):
      r = r_0 + i
      for j in range(0,3):
        c = c_0 + j

        if r >= 0 and r < 8 and c >= 0 and c < 8 :
          moves |= Square(row_col_to_idx(r,c)).as_uint64()

    return moves

  #this function covers the tricky horizontal discover check from enp captures, example here
  #https://lichess.org/analysis/8/4p3/8/2KP3q/8/1k6/8/8_b_-_-_0_1#2
  def spec_enp_legalcheck(self, cb, capt_from):
    #check if rook/queen on rank
    row, col = idx_to_row_col(capt_from)

    full_row = np.uint8(0xFF)
    full_row_idx = np.uint64(full_row << (row - 1) * 8)

    kings = cb.pieces['k']
    queens = cb.pieces['q']
    our_king = cb.pieces['K']

    if (kings | queens) & full_row_idx == 0 : return True
    else :
      lost_piece_sq = cb.enpassant_sq - 8

      cap_64 = np.uint64(1) << np.uint64(capt_from)
      cap_lost_64 = np.uint64(1) << np.uint64(lost_piece_sq)

      #get all attacks rays without the enp pieces
      all_atc_idc = cb.get_pieces_idx_from_uint(kings | queens)
      occ_no_enp_pieces = (cb.get_all_pieces() | cb.get_all_pieces(ours=False)) & ~(cap_64 | cap_lost_64)
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
      return np.uint64(0)

    attack_mask = np.uint64(0)

    pin_at = -1
    pin_attackray = np.uint64(0)

    for mdir in m_dirs:
      row, col = idx_to_row_col(attacker_sq)

      found_ray = False
      found_pin = False

      no_pin = False #if block by own piece

      pin_attackray |= np.uint64(1) << np.uint64(attacker_sq)

      while True :
        row += mdir[1]
        col += mdir[0]

        if row <  0 or row > 7 or col <  0 or col > 7  : break

        new_idx = row_col_to_idx(row, col)

        if new_idx == ksq:
          found_ray = True
          break

        n_sq_64 = np.uint64(1) << np.uint64(new_idx)

        if n_sq_64 & enemy_pieces != 0 : no_pin = True

        if our_pieces & n_sq_64 != 0 and not found_pin and not no_pin :
          found_pin = True
          pin_at = new_idx
          pin_from = attacker_sq

        attack_mask |= n_sq_64
        pin_attackray |= n_sq_64

      if found_ray:
        break
      else:
        attack_mask = np.uint64(0)
        pin_at = -1
        pin_attackray = np.uint64(0)

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

    if len(cb.get_pieces_idx_from_uint(enemy_king_pos)) == 0 :
      cb.print_console()

    enemy_king_idx = cb.get_pieces_idx_from_uint(enemy_king_pos)[0]

    our_pieces = cb.get_all_pieces()
    enemy_pieces = cb.get_all_pieces(ours=False)
    occ = our_pieces | enemy_pieces
    occ_no_king = occ - king_pos

    n_checkers = 0
    attacking_mask = np.uint64(0) # all enemy attack squares, covering castle and similar
    attacking_mask_noking = np.uint64(0) # same but with no king, need this to calculate correct king moves out of check

    push_mask = np.uint64(0) #attack squares between slider and king
    capture_mask = np.uint64(0) #attack squares where
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
        capture_mask |= np.uint64(1) << np.uint64(p_idx)

    #knights
    kn_idcs = cb.get_pieces_idx_from_uint(enemy_knights)
    for kn_idx in kn_idcs :
      attacks = self.knight_attacks[kn_idx]
      attacking_mask |= attacks
      attacking_mask_noking |= attacks
      if attacks & king_pos != 0 :
        n_checkers += 1
        knight_attacking_king = True
        capture_mask |= np.uint64(1) << np.uint64(kn_idx)

    #bishops
    b_idcs = cb.get_pieces_idx_from_uint(enemy_bishops)
    for b_idx in b_idcs:
      attacks = self.sliding_attacktables.query_bishop_attacks(b_idx, occ)
      attacks_noking = self.sliding_attacktables.query_bishop_attacks(b_idx, occ_no_king)
      attacking_mask |= attacks
      attacking_mask_noking |= attacks_noking

      if self.sliding_attacktables.query_bishop_attacks(b_idx, np.uint64(0)) & king_pos != 0 :
        push, pin = self.calc_pushmoves(our_pieces, enemy_pieces, king_idx, b_idx, 'b')  # where we can block
        pins.append(pin)
        if attacks & king_pos != 0:
          n_checkers += 1
          push_mask |= push
          capture_mask |= np.uint64(1) << np.uint64(b_idx)

    #rooks
    r_idcs = cb.get_pieces_idx_from_uint(enemy_rooks)
    for r_idx in r_idcs:
      attacks = self.sliding_attacktables.query_rook_attacks(r_idx, occ)
      attacks_noking = self.sliding_attacktables.query_rook_attacks(r_idx, occ_no_king)
      attacking_mask |= attacks
      attacking_mask_noking |= attacks_noking

      if self.sliding_attacktables.query_rook_attacks(r_idx, np.uint64(0)) & king_pos != 0:
        push, pin = self.calc_pushmoves(our_pieces, enemy_pieces, king_idx, r_idx, 'r')  # where we can block
        pins.append(pin)
        if attacks & king_pos != 0:
          n_checkers += 1
          push_mask |= push
          capture_mask |= np.uint64(1) << np.uint64(r_idx)

    #queens
    q_idcs = cb.get_pieces_idx_from_uint(enemy_queens)
    for q_idx in q_idcs:
      attacks = self.sliding_attacktables.query_rook_attacks(q_idx, occ)
      attacks |= self.sliding_attacktables.query_bishop_attacks(q_idx, occ)

      attacks_noking = self.sliding_attacktables.query_rook_attacks(q_idx, occ_no_king)
      attacks_noking |= self.sliding_attacktables.query_bishop_attacks(q_idx, occ_no_king)

      attacking_mask |= attacks
      attacking_mask_noking |= attacks_noking

      if (self.sliding_attacktables.query_bishop_attacks(q_idx, np.uint64(0)) & king_pos != 0) or \
         (self.sliding_attacktables.query_rook_attacks(q_idx, np.uint64(0)) & king_pos != 0) :
        push, pin = self.calc_pushmoves(our_pieces, enemy_pieces, king_idx, q_idx, 'q')  # where we can block
        pins.append(pin)
        if attacks & king_pos != 0:
          n_checkers += 1
          push_mask |= push
          capture_mask |= np.uint64(1) << np.uint64(q_idx)

    if knight_attacking_king :
      push_mask = np.uint64(0)

    return {
    'n_checkers' : n_checkers,
    'attack_mask' : attacking_mask,
    'attack_mask_noking' :attacking_mask_noking,
    'push_mask' : push_mask,
    'capture_mask': capture_mask,
    'pins' : pins
    }

  def generate_legal_moves(self, cb):
    all_moves = ChessMoveList()

    attackinfo = self.get_enemy_attackinfo(cb)

    n_checkers = attackinfo['n_checkers']
    attack_mask = attackinfo['attack_mask']
    attack_mask_noking = attackinfo['attack_mask_noking']
    capture_mask = attackinfo['capture_mask']

    our_pieces = cb.get_all_pieces()
    enemy_pieces = cb.get_all_pieces(ours=False)
    all_pieces = our_pieces | enemy_pieces

    king_square = cb.get_pieces_idx('K')[0]
    king_moves = self.get_kingmoves(king_square)

    #bug, the king can capture anywhere on the board if he's under check
    legal_king_moves = king_moves & (~attack_mask_noking & ~our_pieces & (~enemy_pieces & ~attack_mask))

    m_idc = cb.get_pieces_idx_from_uint(legal_king_moves)

    for k_move_idx in m_idc: all_moves.add_move(ChessMove(king_square, k_move_idx, ptype='K'))

    if n_checkers >= 2 :
      return all_moves #there's no other options

    king_in_check = True if n_checkers >= 1 else False

    enemy_king_pos = cb.pieces['k']

    p_idcs = cb.get_pieces_idx('P')
    self.append_pawnmoves(cb, all_moves, all_pieces, p_idcs, king_in_check, attackinfo, enemy_king_pos)

    kn_idcs = cb.get_pieces_idx('N')
    self.append_knightmoves(cb, all_moves, our_pieces, enemy_pieces, kn_idcs, king_in_check, attackinfo, enemy_king_pos)

    b_idcs = cb.get_pieces_idx('B')
    self.append_bishopmoves(cb, all_moves, our_pieces, enemy_pieces, b_idcs, king_in_check, attackinfo, enemy_king_pos)

    r_idcs = cb.get_pieces_idx('R')
    self.append_rookmoves(cb, all_moves, our_pieces, enemy_pieces, r_idcs, king_in_check, attackinfo, enemy_king_pos)

    q_idcs = cb.get_pieces_idx('Q')
    self.append_queenmoves(cb, all_moves, our_pieces, enemy_pieces, q_idcs, king_in_check, attackinfo, enemy_king_pos)

    #castle moves
    if not king_in_check :

      csq_00_64 = np.uint64(1) << np.uint64(5) | np.uint64(1) << np.uint64(6)
      csq_000_64 = np.uint64(1) << np.uint64(2) | np.uint64(1) << np.uint64(3)

      #we're able to castle, there's nothing there and there's nothing attacking connected castle squares. its then legal
      if cb.castling.we_00() :
        if csq_00_64 & all_pieces == 0 and csq_00_64 &  attack_mask  == 0 : all_moves.add_move(ChessMove(4, 6, 'K', 'O-O'))
      if cb.castling.we_000() :
        if csq_000_64 & all_pieces == 0 and csq_000_64 & attack_mask == 0 : all_moves.add_move(ChessMove(4, 2, 'K', 'O-O-O'))

    return all_moves

  def append_queenmoves(self, cb, chessmove_list, our_pieces, enemy_pieces, b_idcs, king_incheck, attackinfo, enemy_king_pos):
    ptype ='Q'

    pins = attackinfo['pins']
    push_mask = attackinfo['push_mask']
    capture_mask = attackinfo['capture_mask']

    occ = our_pieces | enemy_pieces

    for idx in b_idcs :
      idx_64 = np.uint64(1) << np.uint64(idx)
      attacks = (self.sliding_attacktables.query_rook_attacks(idx, occ) | self.sliding_attacktables.query_bishop_attacks(idx, occ)) \
                & ~(our_pieces | enemy_king_pos)

      is_pinned = False

      if king_incheck :
        for pin in pins:
          if (np.uint64(1) << np.uint64(pin[0])) & idx_64 != 0:
            is_pinned = True

        if is_pinned : continue

        if capture_mask != 0 and attacks & capture_mask != 0: add_capture_mask = True
        else : add_capture_mask = False

        attacks &= push_mask

        if add_capture_mask : attacks |= capture_mask

        attack_idcs = cb.get_pieces_idx_from_uint(attacks)
        [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

      else :
        pin_index  = -1

        for index, pin in enumerate(pins):
          if (np.uint64(1) << np.uint64(pin[0])) & idx_64 != 0:
            pin_index = index
            is_pinned = True
            break

        if is_pinned :
          _,_from_ray = pins[pin_index]
          attacks &= _from_ray

        attack_idcs = cb.get_pieces_idx_from_uint(attacks)
        [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

  def append_rookmoves(self, cb, chessmove_list, our_pieces, enemy_pieces, b_idcs, king_incheck, attackinfo, enemy_king_pos):
    ptype ='R'

    pins = attackinfo['pins']
    push_mask = attackinfo['push_mask']
    capture_mask = attackinfo['capture_mask']

    occ = our_pieces | enemy_pieces

    for idx in b_idcs :
      idx_64 = np.uint64(1) << np.uint64(idx)
      attacks = self.sliding_attacktables.query_rook_attacks(idx, occ) & ~(our_pieces | enemy_king_pos)
      is_pinned = False

      if king_incheck :
        for pin in pins:
          if (np.uint64(1) << np.uint64(pin[0])) & idx_64 != 0:
            is_pinned = True

        if is_pinned : continue

        if capture_mask != 0 and attacks & capture_mask != 0: add_capture_mask = True
        else : add_capture_mask = False

        attacks &= push_mask

        if add_capture_mask : attacks |= capture_mask

        attack_idcs = cb.get_pieces_idx_from_uint(attacks)
        [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

      else :
        pin_index  = -1

        for index, pin in enumerate(pins):
          if (np.uint64(1) << np.uint64(pin[0])) & idx_64 != 0:
            pin_index = index
            is_pinned = True
            break

        if is_pinned :
          _,_from_ray = pins[pin_index]
          attacks &= _from_ray

        attack_idcs = cb.get_pieces_idx_from_uint(attacks)
        [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

  def append_bishopmoves(self, cb, chessmove_list, our_pieces, enemy_pieces, b_idcs, king_incheck, attackinfo, enemy_king_pos):
    ptype ='B'

    pins = attackinfo['pins']
    push_mask = attackinfo['push_mask']
    capture_mask = attackinfo['capture_mask']

    occ = our_pieces | enemy_pieces

    for idx in b_idcs :
      idx_64 = np.uint64(1) << np.uint64(idx)
      attacks = self.sliding_attacktables.query_bishop_attacks(idx, occ) & ~(our_pieces | enemy_king_pos)
      is_pinned = False

      if king_incheck :
        for pin in pins:
          if (np.uint64(1) << np.uint64(pin[0])) & idx_64 != 0:
            is_pinned = True

        if is_pinned : continue

        if capture_mask != 0 and attacks & capture_mask != 0: add_capture_mask = True
        else : add_capture_mask = False

        attacks &= push_mask

        if add_capture_mask : attacks |= capture_mask

        attack_idcs = cb.get_pieces_idx_from_uint(attacks)
        [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

      else :
        pin_index  = -1

        for index, pin in enumerate(pins):
          if (np.uint64(1) << np.uint64(pin[0])) & idx_64 != 0:
            pin_index = index
            is_pinned = True
            break

        if is_pinned :
          _,_from_ray = pins[pin_index]
          attacks &= _from_ray

        attack_idcs = cb.get_pieces_idx_from_uint(attacks)
        [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

  def append_knightmoves(self, cb, chessmove_list, our_pieces, enemy_pieces, kn_idcs, king_incheck, attackinfo, enemy_king_pos):
    ptype = 'N'

    pins = attackinfo['pins']
    push_mask = attackinfo['push_mask']
    capture_mask = attackinfo['capture_mask']

    for idx in kn_idcs :
      is_pinned = False

      idx_64 = np.uint64(1) << np.uint64(idx)

      for pin in pins:
        if (np.uint64(1) << np.uint64(pin[0])) & idx_64 != 0:
          is_pinned = True

      if is_pinned : continue

      attacks = self.knight_attacks[idx] &  ~(our_pieces | enemy_king_pos)

      if king_incheck :
        attacks = (push_mask & attacks) | (capture_mask & attacks)


      attack_idcs = cb.get_pieces_idx_from_uint(attacks)
      [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

  def append_pawnmoves(self, cb, chessmove_list, occ, p_idcs, king_incheck, attackinfo, enemy_king_pos):
      one_move = 8
      two_move = 16

      pins = attackinfo['pins']
      push_mask = attackinfo['push_mask']
      capture_mask = attackinfo['capture_mask']

      enemy_pieces = cb.get_all_pieces(ours=False)

      enp_sq = np.uint64(cb.enpassant_sq)

      ptype = 'P'

      for idx in p_idcs:
        idx_64 = np.uint64(1) << np.uint64(idx)

        n_sq_onemove = np.uint64(1) << np.uint64(idx + 8)
        n_sq_twomove = np.uint64(1) << np.uint64(idx + 16)

        is_pinned = False

        if king_incheck :
          for pin in pins :
            if (np.uint64(1) << np.uint64(pin[0])) & idx_64 != 0 :
              is_pinned = True

          if is_pinned : continue

          #bug, this captured our own king :D mb could be issues in future, not 100 %
          if n_sq_onemove & push_mask != 0 :

            chessmove_list.add_move(ChessMove(idx, idx + one_move, ptype=ptype))
          if n_sq_twomove & push_mask != 0 :
            if idx <= 15:
              if n_sq_twomove & occ == 0 and \
                     n_sq_onemove & occ == 0:
                chessmove_list.add_move(ChessMove(idx, idx + two_move, ptype=ptype))

          attack_64 = self.pawn_attacks[idx]
          a_sq_idx = cb.get_pieces_idx_from_uint(attack_64)
          for a_sq in a_sq_idx :
            if enp_sq == a_sq :
              chessmove_list.add_move(ChessMove(idx, a_sq, ptype=ptype, spec_action='enp'))

            elif (np.uint64(1) << np.uint64(a_sq)) & capture_mask != 0 :
              chessmove_list.add_move(ChessMove(idx, a_sq, ptype=ptype))

          continue #dont add normal moves

        pin_index  = -1

        for index, pin in enumerate(pins):
          if (np.uint64(1) << np.uint64(pin[0])) & idx_64 != 0:
            pin_index = index
            is_pinned = True
            break

        attack_64 = self.pawn_attacks[idx] & ~enemy_king_pos

        if is_pinned :
          _, _from_ray = pins[pin_index]
          attack_64 &= _from_ray

        a_sq_idx = cb.get_pieces_idx_from_uint(attack_64)

        for a_sq in a_sq_idx:
          if enp_sq == a_sq:
            if self.spec_enp_legalcheck(cb, a_sq) :
              chessmove_list.add_move(ChessMove(idx, a_sq, ptype=ptype, spec_action='enp'))

          if (np.uint64(1) << np.uint64(a_sq)) & enemy_pieces != 0: chessmove_list.add_move(
            ChessMove(idx, a_sq, ptype=ptype))

        if is_pinned : continue

        # add all one moves
        if n_sq_onemove & occ == 0:
          chessmove_list.add_move(ChessMove(idx, idx + one_move, ptype=ptype))

        # add all two moves
        if idx <= 15:
          if n_sq_twomove & occ == 0 and \
                  n_sq_onemove & occ == 0: chessmove_list.add_move(
            ChessMove(idx, idx + two_move, ptype=ptype))

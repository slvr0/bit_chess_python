from chess_square import *
from chess_board import ChessBoard
from utils import *
from chess_attack_tables import *
from chess_move import ChessMove, ChessMoveList

#implementation will be influenced by
#https://peterellisjones.com/posts/generating-legal-chess-moves-efficiently/

#i will start at generating legal king moves

from time import time

class MoveGenerator :
  def __init__(self):
    self.sliding_attacktables = SlidingAttackTables()
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
    pin_mask = np.uint64(0)

    for mdir in m_dirs:
      row, col = idx_to_row_col(attacker_sq)

      found_ray = False
      found_pin = False

      no_pin = False #if block by own piece

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
          pin_mask |= n_sq_64

        attack_mask |= n_sq_64

      if found_ray:
        break
      else:
        attack_mask = np.uint64(0)
        pin_mask = np.uint64(0)

    return attack_mask, pin_mask

  #calculate rays from square to king square, e.g. attacking path for a rook,bishop to the king
  def get_capture_push_masks(self, attack_mask, king_square, cb):
    attack_idcs = cb.get_pieces_idx_from_uint(attack_mask)

    push_mask = np.uint64(0)
    capture_mask = np.uint64(0)
    our_pieces = cb.get_all_pieces()

    for a_idx in attack_idcs :
      occupied_piecetype = cb.square_occupied_by(a_idx)
      if occupied_piecetype == 'r' or occupied_piecetype == 'b' or occupied_piecetype == 'q' :
        push, pin =self.calc_pushmoves(our_pieces, king_square, a_idx, occupied_piecetype)
        push_mask |= push

      elif occupied_piecetype == 'n' :
        capture_mask  |= np.uint64(1)  << a_idx

    return push_mask, capture_mask

  #bug remaining, we cant calculate enemy pawn attacks since they are reversed direction
  def get_enemy_attackinfo(self, cb ):
    king_pos = cb.pieces['K']
    king_idx = cb.get_pieces_idx_from_uint(king_pos)[0]

    enemy_pawns = cb.pieces['p']
    enemy_knights = cb.pieces['n']
    enemy_bishops = cb.pieces['b']
    enemy_queens = cb.pieces['q']
    enemy_rooks = cb.pieces['r']

    our_pieces = cb.get_all_pieces()
    enemy_pieces = cb.get_all_pieces(ours=False)
    occ = our_pieces | enemy_pieces
    occ_no_king = occ - king_pos

    n_checkers = 0
    attacking_mask = np.uint64(0) # all enemy attack squares, covering castle and similar
    attacking_mask_noking = np.uint64(0) # same but with no king, need this to calculate correct king moves out of check

    push_mask = np.uint64(0) #attack squares between slider and king
    capture_mask = np.uint64(0) #attack squares where
    pin_mask = np.uint64(0) #attack squares where pieces cannot move

    #pawns
    p_idcs = cb.get_pieces_idx_from_uint(enemy_pawns)
    for p_idx in p_idcs :
      attacks = self.pawn_attacks.pawn_attacks_rev[p_idx]
      attacking_mask |= attacks
      attacking_mask_noking |= attacks
      if attacks & king_pos != 0:
        n_checkers += 1
        push_mask |= attacks
        capture_mask |= np.uint64(1) << np.uint64(p_idx)

    #knights
    kn_idcs = cb.get_pieces_idx_from_uint(enemy_knights)
    for kn_idx in kn_idcs :
      attacks = self.knight_attacks[kn_idx]
      attacking_mask |= attacks
      attacking_mask_noking |= attacks
      if attacks & king_pos != 0 :
        n_checkers += 1
        push_mask |= attacks
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
        pin_mask |= pin
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
        pin_mask |= pin
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
        pin_mask |= pin
        if attacks & king_pos != 0:
          n_checkers += 1
          push_mask |= push
          capture_mask |= np.uint64(1) << np.uint64(q_idx)

    return {
    'n_checkers' : n_checkers,
    'attack_mask' : attacking_mask,
    'attack_mask_noking' :attacking_mask_noking,
    'push_mask' : push_mask,
    'capture_mask': capture_mask,
    'pin_mask' : pin_mask
    }

  def generate_pseudo_legal_moves(self, cb):
    t1 = time()

    all_moves = ChessMoveList()

    our_pieces = cb.get_all_pieces()
    enemy_pieces = cb.get_all_pieces(ours=False)
    all_pieces = our_pieces | enemy_pieces

    #kingmoves
    king_square = cb.get_pieces_idx('K')[0]
    king_moves = self.get_kingmoves(king_square)
    legal_king_moves = king_moves & ~all_pieces #'cheyck' if the piece is defended

    m_idc = cb.get_pieces_idx_from_uint(legal_king_moves)

    for k_move_idx in m_idc: all_moves.add_move(ChessMove(king_square, k_move_idx, ptype='K'))




  def generate_legal_moves(self, cb):

    t1 = time()

    all_moves = ChessMoveList()

    attackinfo = self.get_enemy_attackinfo(cb)

    n_checkers = attackinfo['n_checkers']
    attack_mask = attackinfo['attack_mask']
    attack_mask_noking = attackinfo['attack_mask_noking']
    push_mask = attackinfo['push_mask']
    capture_mask = attackinfo['capture_mask']
    pin_mask = attackinfo['pin_mask']

    our_pieces = cb.get_all_pieces()
    enemy_pieces = cb.get_all_pieces(ours=False)
    all_pieces = our_pieces | enemy_pieces

    king_square = cb.get_pieces_idx('K')[0]
    king_moves = self.get_kingmoves(king_square)

    legal_king_moves = king_moves & ~attack_mask_noking & ~all_pieces

    m_idc = cb.get_pieces_idx_from_uint(legal_king_moves)

    for k_move_idx in m_idc: all_moves.add_move(ChessMove(king_square, k_move_idx, ptype='K'))

    if n_checkers >= 2 :
      return all_moves #there's no other options

    king_in_check = True if n_checkers == 1 else False

    p_idcs = cb.get_pieces_idx('P')
    self.append_pawnmoves(cb, all_moves, all_pieces, p_idcs, king_in_check, attackinfo)

    kn_idcs = cb.get_pieces_idx('N')
    self.append_knightmoves(cb, all_moves, our_pieces, enemy_pieces, kn_idcs, king_in_check, attackinfo)

    print(time()-t1)
    all_moves.print()

    return []

  def append_bishopmoves(self, cb, chessmove_list, our_pieces, enemy_pieces, b_idcs, king_incheck, attackinfo):
    ptype ='B'

    pin_mask = attackinfo['pin_mask']
    push_mask = attackinfo['push_mask']
    capture_mask = attackinfo['capture_mask']

    occ = our_pieces | enemy_pieces

    for idx in b_idcs :
      idx_64 = np.uint64(1) << np.uint64(idx)
      if idx_64 & pin_mask != 0 : continue

      attacks = self.sliding_attacktables.query_bishop_attacks(idx, occ)

      if capture_mask != 0 and attacks & capture_mask != 0: add_capture_mask = True
      else : add_capture_mask = False

      if push_mask != 0 :
        attacks &= push_mask

      if add_capture_mask : attacks |= capture_mask

      attack_idcs = cb.get_pieces_idx_from_uint(attacks)
      [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]


  def append_knightmoves(self, cb, chessmove_list, our_pieces, enemy_pieces, kn_idcs, king_incheck, attackinfo):
    ptype = 'N'

    pin_mask = attackinfo['pin_mask']
    push_mask = attackinfo['push_mask']
    capture_mask = attackinfo['capture_mask']

    for idx in kn_idcs :
      idx_64 = np.uint64(1) << np.uint64(idx)
      if idx_64 & pin_mask != 0 : continue

      attacks = self.knight_attacks[idx]

      if king_incheck :
        attacks = (push_mask & attacks) | (capture_mask & attacks)
      else :
        attacks &= ~our_pieces

      attack_idcs = cb.get_pieces_idx_from_uint(attacks)
      [chessmove_list.add_move(ChessMove(_from=idx, to=n_idx, ptype=ptype)) for n_idx in attack_idcs]

  def append_pawnmoves(self, cb, chessmove_list, occ, p_idcs, king_incheck, attackinfo):
      one_move = 8
      two_move = 16

      pin_mask = attackinfo['pin_mask']
      push_mask = attackinfo['push_mask']
      capture_mask = attackinfo['capture_mask']

      enemy_pieces = cb.get_all_pieces(ours=False)

      ptype = 'P'

      for idx in p_idcs:
        idx_64 = np.uint64(1) << np.uint64(idx)

        n_sq_onemove = np.uint64(1) << np.uint64(idx + 8)
        n_sq_twomove = np.uint64(1) << np.uint64(idx + 16)

        if king_incheck :
          if pin_mask & idx_64 != 0 : continue #pawn is in absolute pin,

          if n_sq_onemove & push_mask != 0 : chessmove_list.add_move(ChessMove(idx, idx + one_move, ptype=ptype))
          if n_sq_twomove & push_mask != 0 :
            if idx <= 15:

              if n_sq_twomove & occ == 0 and \
                     n_sq_onemove & occ == 0:
                chessmove_list.add_move(ChessMove(idx, idx + two_move, ptype=ptype))

          attack_64 = self.pawn_attacks[idx]
          a_sq_idx = cb.get_pieces_idx_from_uint(attack_64)
          for a_sq in a_sq_idx :
            if (np.uint64(1) << np.uint64(a_sq)) & capture_mask != 0 : chessmove_list.add_move(ChessMove(idx, a_sq, ptype=ptype))

          continue #dont add normal moves

        attack_64 = self.pawn_attacks[idx]
        a_sq_idx = cb.get_pieces_idx_from_uint(attack_64)
        for a_sq in a_sq_idx:
          if (np.uint64(1) << np.uint64(a_sq)) & enemy_pieces != 0: chessmove_list.add_move(
            ChessMove(idx, a_sq, ptype=ptype))

        if pin_mask & idx_64 != 0: continue

        # add all one moves
        if n_sq_onemove & occ == 0:
          chessmove_list.add_move(ChessMove(idx, idx + one_move, ptype=ptype))

        # add all two moves
        if idx <= 15:
          if n_sq_twomove & occ == 0 and \
                  n_sq_onemove & occ == 0: chessmove_list.add_move(
            ChessMove(idx, idx + two_move, ptype=ptype))





  # our_pawns = cb.pieces['P']
  # our_knights = cb.pieces['N']
  # our_bishops = cb.pieces['B']
  # our_queens = cb.pieces['Q']
  # our_rooks = cb.pieces['R']
  # our_king = cb.pieces['K']
  #
  # enemy_pawns = cb.pieces['p']
  # enemy_knights = cb.pieces['n']
  # enemy_bishops = cb.pieces['b']
  # enemy_queens = cb.pieces['q']
  # enemy_rooks = cb.pieces['r']
  # enemy_king = cb.pieces['k']
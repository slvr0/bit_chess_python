from chess_square import *
from chess_board import ChessBoard
from utils import *
from chess_attack_tables import *
from chess_move import ChessMove

#implementation will be influenced by
#https://peterellisjones.com/posts/generating-legal-chess-moves-efficiently/

#i will start at generating legal king moves

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


  #check if king is in check. returns number of attackers
  def is_incheck(self, occ, king_pos, cb ):
    enemy_pawns = cb.pieces['p']
    enemy_knights = cb.pieces['n']
    enemy_bishops = cb.pieces['b']
    enemy_queens = cb.pieces['q']
    enemy_rooks = cb.pieces['r']
    n_attackers = 0

    checking_mask = np.uint64(0)

    if self.knight_attacks[king_pos] & enemy_knights :
      n_attackers += 1

    pawn_idc = cb.get_pieces_idx('p')
    pawn_attacks = np.uint64(0)
    for p_idx in pawn_idc : pawn_attacks |= self.pawn_attacks[p_idx]

    if np.uint64(pawn_attacks) & np.uint64(1 << king_pos) != 0 :
      n_attackers += 1
      checking_mask |= np.uint64(1) << np.uint64(p_idx)

    #ok now check sliders
    rook_attacks_rev = self.sliding_attacktables.query_rook_attacks(king_pos, occ)
    if rook_attacks_rev & enemy_rooks != 0 :
      n_attackers += 1
      checking_mask |= rook_attacks_rev & enemy_rooks

    bishop_attacks_rev = self.sliding_attacktables.query_bishop_attacks(king_pos, occ)
    if bishop_attacks_rev & enemy_bishops != 0 :
      n_attackers += 1
      checking_mask |= bishop_attacks_rev & enemy_bishops

    queen_attacks_rev = rook_attacks_rev | bishop_attacks_rev
    if queen_attacks_rev & enemy_queens != 0 :
      n_attackers += 1
      checking_mask |= queen_attacks_rev & enemy_queens

    return n_attackers, checking_mask

  #double purpose function, we use it to get all enemy attack squares,
  #with and without king in occupancy squares
  #then we can use it both for seing legal castle moves, pins squares and king moves
  def get_attack_squares(self, occ, king_pos, cb = ChessBoard):
    enemy_pawns = cb.pieces['p']
    enemy_knights = cb.pieces['n']
    enemy_bishops = cb.pieces['b']
    enemy_queens = cb.pieces['q']
    enemy_rooks = cb.pieces['r']
    enemy_king = cb.pieces['k']

    occ_no_king = (cb.get_all_pieces() | cb.get_all_pieces(ours=False)) & ~np.uint64(1 << king_pos)

    pawn_idc = cb.get_pieces_idx('p')
    pawn_attacks = np.uint64(0)
    for p_idx in pawn_idc : pawn_attacks |= self.pawn_attacks[p_idx]

    #we want a special entry for knight checks, the other attacks will be used to calculate pins, these squares
    #should not contribute to that calculation
    knight_attacks = np.uint64(0)
    knight_idc = cb.get_pieces_idx('n')
    for n_idx in knight_idc : knight_attacks |= self.knight_attacks[n_idx]

    rook_attacks = np.uint64(0)
    rook_attacks_noking = np.uint64(0)

    rook_idc = cb.get_pieces_idx('r')
    for r_idx in rook_idc :
      rook_attacks |= self.sliding_attacktables.query_rook_attacks(r_idx, occ)
      rook_attacks_noking |= self.sliding_attacktables.query_rook_attacks(r_idx, occ_no_king)

    bishop_idc = cb.get_pieces_idx('b')
    bishop_attacks = np.uint64(0)
    bishop_attacks_noking = np.uint64(0)

    for b_idx in bishop_idc :
      bishop_attacks |= self.sliding_attacktables.query_bishop_attacks(b_idx, occ)
      bishop_attacks_noking |= self.sliding_attacktables.query_bishop_attacks(b_idx, occ_no_king)

    queen_idc = cb.get_pieces_idx('q')
    queen_attacks = np.uint64(0)
    queen_attacks_noking = np.uint64(0)

    for q_idx in queen_idc :
      q_attacks = self.sliding_attacktables.query_rook_attacks(q_idx, occ) | \
                  self.sliding_attacktables.query_bishop_attacks(q_idx, occ)

      q_attacks_noking = self.sliding_attacktables.query_rook_attacks(q_idx, occ_no_king) | \
                  self.sliding_attacktables.query_bishop_attacks(q_idx, occ_no_king)

      queen_attacks |= q_attacks
      queen_attacks_noking |= q_attacks_noking

    all_attacks = pawn_attacks | bishop_attacks | rook_attacks | queen_attacks
    all_attacks_noking = pawn_attacks | knight_attacks | bishop_attacks_noking | rook_attacks_noking | queen_attacks_noking

    return all_attacks, all_attacks_noking, knight_attacks

  def generate_legal_moves(self, cb = ChessBoard):
    all_moves = []
    our_pawns = cb.pieces['P']
    our_knights = cb.pieces['N']
    our_bishops = cb.pieces['B']
    our_queens = cb.pieces['Q']
    our_rooks = cb.pieces['R']
    our_king = cb.pieces['K']

    enemy_pawns = cb.pieces['p']
    enemy_knights = cb.pieces['n']
    enemy_bishops = cb.pieces['b']
    enemy_queens = cb.pieces['q']
    enemy_rooks = cb.pieces['r']
    enemy_king = cb.pieces['k']

    our_pieces = cb.get_all_pieces(ours=True)
    enemy_pieces = cb.get_all_pieces(ours=False)
    all_pieces = our_pieces | enemy_pieces

    king_square = cb.get_pieces_idx('K')[0]
    n_checkers, checking_mask = self.is_incheck(all_pieces, king_square, cb)

    all_attacks, all_attacks_noking, knight_attacks = self.get_attack_squares(all_pieces, king_square, cb)

    #cb.print_bitboard(all_attacks_noking)
    k_moves = self.get_kingmoves(king_square)
    legal_king_moves = (k_moves & ~all_attacks_noking) & ~all_pieces
    if n_checkers >= 2 :
      m_idc = cb.get_pieces_idx_from_uint(legal_king_moves)
      for k_move_idx in m_idc : all_moves.append(ChessMove(king_square, k_move_idx, ptype='K'))

    elif n_checkers == 1 :
      #estimate if we're checked by a knight
      kn_attack = knight_attacks & checking_mask

      #move
      m_idc = cb.get_pieces_idx_from_uint(legal_king_moves)
      for k_move_idx in m_idc: all_moves.append(ChessMove(king_square, k_move_idx, ptype='K'))

      #capture, check if guarded, then check if we can reach
      if (all_attacks & checking_mask) != 0 and (legal_king_moves & checking_mask) != 0 :
        all_moves.append(ChessMove(king_square, cb.get_pieces_idx_from_uint(checking_mask)[0], ptype='K')) #slightly ugly

      #if its not a knight, we can try blocking it
      if not kn_attack:
        #ray squares between attacker and king
        #cb.print_bitboard(all_attacks)








    
    
    
    
    
    






    return []
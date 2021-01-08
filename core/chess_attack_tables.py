import numpy as np
from core.chess_square import Square
from core.chess_board import ChessBoard

from core.chess_square import Square, _idx_64, idx_to_row_col, row_col_to_idx
from core.utils import CombinationSolver

import ctypes

from time import time
#some help understanding
#https://stackoverflow.com/questions/30680559/how-to-find-magic-bitboards

#the idea is :
#with a given attack table for a square that we call blocker mask
#find all blockers currently occupiying this grid
#we call that blocker board.
#generate a move board from this
#use the magic bitboard algorithm to HASH the blocker board configuration and save a lookup to the move board

import warnings

class IndexedPawnAttacks :
  def __init__(self):

    a0 = [0] * 8

    our_pawn_attacks = [2**9, 2**8 + 2**10, 2**9 + 2**11, 2**10 + 2**12, 2**11 + 2**13, 2**12 + 2**14, 2**13 + 2**15, 2**14]
    for row in range(1, 7) :
      [our_pawn_attacks.append(v) for v in [our_pawn_attacks[i] << 8*row for i in range(8)]]

    self.pawn_attacks = np.concatenate([our_pawn_attacks, a0], axis=0)

    pawn_atk_tbl = [2**1, 2**0 + 2**2, 2**1 + 2**3, 2**2 + 2**4, 2**3 + 2**5, 2**4 + 2**6, 2**5 + 2**7, 2**6]

    for row in range(1,7) :
        [pawn_atk_tbl.append(v) for v in [pawn_atk_tbl[i] << 8*row for i in range(8)]]

    pawn_atk_tbl = np.array(pawn_atk_tbl)

    pawn_atk_tbl = np.concatenate([a0, pawn_atk_tbl], axis=0)
    self.pawn_attacks_rev = [np.uint64(v) for v in pawn_atk_tbl]

    self.pawn_attacks = [np.uint64(v) for v in self.pawn_attacks] #convert entries to np.uint64

  def __getitem__(self, idx):
    assert idx >= 0 and idx < 64

    return self.pawn_attacks[idx]

class IndexedKnightAttacks :
  def __init__(self):
    self.knight_attacks = [
    0x0000000000020400, 0x0000000000050800, 0x00000000000A1100,
    0x0000000000142200, 0x0000000000284400, 0x0000000000508800,
    0x0000000000A01000, 0x0000000000402000, 0x0000000002040004,
    0x0000000005080008, 0x000000000A110011, 0x0000000014220022,
    0x0000000028440044, 0x0000000050880088, 0x00000000A0100010,
    0x0000000040200020, 0x0000000204000402, 0x0000000508000805,
    0x0000000A1100110A, 0x0000001422002214, 0x0000002844004428,
    0x0000005088008850, 0x000000A0100010A0, 0x0000004020002040,
    0x0000020400040200, 0x0000050800080500, 0x00000A1100110A00,
    0x0000142200221400, 0x0000284400442800, 0x0000508800885000,
    0x0000A0100010A000, 0x0000402000204000, 0x0002040004020000,
    0x0005080008050000, 0x000A1100110A0000, 0x0014220022140000,
    0x0028440044280000, 0x0050880088500000, 0x00A0100010A00000,
    0x0040200020400000, 0x0204000402000000, 0x0508000805000000,
    0x0A1100110A000000, 0x1422002214000000, 0x2844004428000000,
    0x5088008850000000, 0xA0100010A0000000, 0x4020002040000000,
    0x0400040200000000, 0x0800080500000000, 0x1100110A00000000,
    0x2200221400000000, 0x4400442800000000, 0x8800885000000000,
    0x100010A000000000, 0x2000204000000000, 0x0004020000000000,
    0x0008050000000000, 0x00110A0000000000, 0x0022140000000000,
    0x0044280000000000, 0x0088500000000000, 0x0010A00000000000,
    0x0020400000000000]

    self.knight_attacks = [np.uint64(v) for v in self.knight_attacks]  # convert entries to np.uint64

  def __getitem__(self, idx):
    assert idx >= 0 and idx < 64

    return self.knight_attacks[idx]

class BishopMagicBitboard :
  def __init__(self):
    self.magic_numbers = \
    [
      0x0008201802242020, 0x0021040424806220, 0x4006360602013080,
      0x0004410020408002, 0x2102021009001140, 0x08C2021004000001,
      0x6001031120200820, 0x1018310402201410, 0x401CE00210820484,
      0x001029D001004100, 0x2C00101080810032, 0x0000082581000010,
      0x10000A0210110020, 0x200002016C202000, 0x0201018821901000,
      0x006A0300420A2100, 0x0010014005450400, 0x1008C12008028280,
      0x00010010004A0040, 0x3000820802044020, 0x0000800405A02820,
      0x8042004300420240, 0x10060801210D2000, 0x0210840500511061,
      0x0008142118509020, 0x0021109460040104, 0x00A1480090019030,
      0x0102008808008020, 0x884084000880E001, 0x040041020A030100,
      0x3000810104110805, 0x04040A2006808440, 0x0044040404C01100,
      0x4122B80800245004, 0x0044020502380046, 0x0100400888020200,
      0x01C0002060020080, 0x4008811100021001, 0x8208450441040609,
      0x0408004900008088, 0x0294212051220882, 0x000041080810E062,
      0x10480A018E005000, 0x80400A0204201600, 0x2800200204100682,
      0x0020200400204441, 0x0A500600A5002400, 0x801602004A010100,
      0x0801841008040880, 0x10010880C4200028, 0x0400004424040000,
      0x0401000142022100, 0x00A00010020A0002, 0x1010400204010810,
      0x0829910400840000, 0x0004235204010080, 0x1002008143082000,
      0x11840044440C2080, 0x2802A02104030440, 0x6100000900840401,
      0x1C20A15A90420200, 0x0088414004480280, 0x0000204242881100,
      0x0240080802809010
    ]
    self.mask = \
    [
      0x0040201008040200, 0x0000402010080400, 0x0000004020100A00, 0x0000000040221400,
      0x0000000002442800, 0x0000000204085000, 0x0000020408102000, 0x0002040810204000,
      0x0020100804020000, 0x0040201008040000, 0x00004020100A0000, 0x0000004022140000,
      0x0000000244280000, 0x0000020408500000, 0x0002040810200000, 0x0004081020400000,
      0x0010080402000200, 0x0020100804000400, 0x004020100A000A00, 0x0000402214001400,
      0x0000024428002800, 0x0002040850005000, 0x0004081020002000, 0x0008102040004000,
      0x0008040200020400, 0x0010080400040800, 0x0020100A000A1000, 0x0040221400142200,
      0x0002442800284400, 0x0004085000500800, 0x0008102000201000, 0x0010204000402000,
      0x0004020002040800, 0x0008040004081000, 0x00100A000A102000, 0x0022140014224000,
      0x0044280028440200, 0x0008500050080400, 0x0010200020100800, 0x0020400040201000,
      0x0002000204081000, 0x0004000408102000, 0x000A000A10204000, 0x0014001422400000,
      0x0028002844020000, 0x0050005008040200, 0x0020002010080400, 0x0040004020100800,
      0x0000020408102000, 0x0000040810204000, 0x00000A1020400000, 0x0000142240000000,
      0x0000284402000000, 0x0000500804020000, 0x0000201008040200, 0x0000402010080400,
      0x0002040810204000, 0x0004081020400000, 0x000A102040000000, 0x0014224000000000,
      0x0028440200000000, 0x0050080402000000, 0x0020100804020000, 0x0040201008040200
    ]
    self.shifts = \
    [
      6, 5, 5, 5, 5, 5, 5, 6,
      5, 5, 5, 5, 5, 5, 5, 5,
      5, 5, 7, 7, 7, 7, 5, 5,
      5, 5, 7, 9, 9, 7, 5, 5,
      5, 5, 7, 9, 9, 7, 5, 5,
      5, 5, 7, 7, 7, 7, 5, 5,
      5, 5, 5, 5, 5, 5, 5, 5,
      6, 5, 5, 5, 5, 5, 5, 6,
    ]

    self.mask = [np.uint64(v) for v in self.mask]  # convert entries to np.uint64
    self.magic_numbers = [np.uint64(v) for v in self.magic_numbers]  # convert entries to np.uint64
    self.shifts = [np.uint64(v) for v in self.shifts]  # convert entries to np.uint64

class RookMagicBitboard :
  def __init__(self):
    self.magic_numbers = \
    [	0x088000102088C001, 0x10C0200040001000, 0x83001041000B2000,
    0x0680280080041000, 0x488004000A080080, 0x0100180400010002,
    0x040001C401021008, 0x02000C04A980C302, 0x0000800040082084,
    0x5020C00820025000, 0x0001002001044012, 0x0402001020400A00,
    0x00C0800800040080, 0x4028800200040080, 0x00A0804200802500,
    0x8004800040802100, 0x0080004000200040, 0x1082810020400100,
    0x0020004010080040, 0x2004818010042800, 0x0601010008005004,
    0x4600808002001400, 0x0010040009180210, 0x020412000406C091,
    0x040084228000C000, 0x8000810100204000, 0x0084110100402000,
    0x0046001A00204210, 0x2001040080080081, 0x0144020080800400,
    0x0840108400080229, 0x0480308A0000410C, 0x0460324002800081,
    0x620080A001804000, 0x2800802000801006, 0x0002809000800800,
    0x4C09040080802800, 0x4808800C00800200, 0x0200311004001802,
    0x0400008402002141, 0x0410800140008020, 0x000080C001050020,
    0x004080204A020010, 0x0224201001010038, 0x0109001108010004,
    0x0282004844020010, 0x8228180110040082, 0x0001000080C10002,
    0x024000C120801080, 0x0001406481060200, 0x0101243200418600,
    0x0108800800100080, 0x4022080100100D00, 0x0000843040600801,
    0x8301000200CC0500, 0x1000004500840200, 0x1100104100800069,
    0x2001008440001021, 0x2002008830204082, 0x0010145000082101,
    0x01A2001004200842, 0x1007000608040041, 0x000A08100203028C,
    0x02D4048040290402]

    self.mask = \
    [	0x000101010101017E, 0x000202020202027C, 0x000404040404047A, 0x0008080808080876,
      0x001010101010106E, 0x002020202020205E, 0x004040404040403E, 0x008080808080807E,
      0x0001010101017E00, 0x0002020202027C00, 0x0004040404047A00, 0x0008080808087600,
      0x0010101010106E00, 0x0020202020205E00, 0x0040404040403E00, 0x0080808080807E00,
      0x00010101017E0100, 0x00020202027C0200, 0x00040404047A0400, 0x0008080808760800,
      0x00101010106E1000, 0x00202020205E2000, 0x00404040403E4000, 0x00808080807E8000,
      0x000101017E010100, 0x000202027C020200, 0x000404047A040400, 0x0008080876080800,
      0x001010106E101000, 0x002020205E202000, 0x004040403E404000, 0x008080807E808000,
      0x0001017E01010100, 0x0002027C02020200, 0x0004047A04040400, 0x0008087608080800,
      0x0010106E10101000, 0x0020205E20202000, 0x0040403E40404000, 0x0080807E80808000,
      0x00017E0101010100, 0x00027C0202020200, 0x00047A0404040400, 0x0008760808080800,
      0x00106E1010101000, 0x00205E2020202000, 0x00403E4040404000, 0x00807E8080808000,
      0x007E010101010100, 0x007C020202020200, 0x007A040404040400, 0x0076080808080800,
      0x006E101010101000, 0x005E202020202000, 0x003E404040404000, 0x007E808080808000,
      0x7E01010101010100, 0x7C02020202020200, 0x7A04040404040400, 0x7608080808080800,
      0x6E10101010101000, 0x5E20202020202000, 0x3E40404040404000, 0x7E80808080808000]

    self.shifts= \
    [
      12, 11, 11, 11, 11, 11, 11, 12,
      11, 10, 10, 10, 10, 10, 10, 11,
      11, 10, 10, 10, 10, 10, 10, 11,
      11, 10, 10, 10, 10, 10, 10, 11,
      11, 10, 10, 10, 10, 10, 10, 11,
      11, 10, 10, 10, 10, 10, 10, 11,
      11, 10, 10, 10, 10, 10, 10, 11,
      12, 11, 11, 11, 11, 11, 11, 12,
    ]

    self.mask = [np.uint64(v) for v in self.mask]  # convert entries to np.uint64
    self.magic_numbers = [np.uint64(v) for v in self.magic_numbers]  # convert entries to np.uint64
    self.shifts = [np.uint64(v) for v in self.shifts]  # convert entries to np.uint64

class SlidingAttackTables :
  def __init__(self):
    self.r_attacktables = np.zeros(shape=(102400), dtype=np.uint64)
    self.b_attacktables = np.zeros(shape=(5248), dtype=np.uint64)
    self.r_offsets = []
    self.b_offsets = []
    self.r_magic = RookMagicBitboard()
    self.b_magic = BishopMagicBitboard()

    self.rook_init = False
    self.bishops_init = False

    self._np_64 = np.uint64(64)

  def query_rook_attacks(self, square, occ):
    assert self.rook_init

    blocker_uint64 = occ & self.r_magic.mask[square ]

    blocker_uint64 *= self.r_magic.magic_numbers[square]

    blocker_uint64 >>= self._np_64 - self.r_magic.shifts[square]

    offset = self.r_offsets[square]

    n_idx = int(offset + blocker_uint64)

    return self.r_attacktables[n_idx]

  def query_bishop_attacks(self, square, occ ):
    assert self.bishops_init

    blocker_uint64 = occ & self.b_magic.mask[square]

    blocker_uint64 *= self.b_magic.magic_numbers[square]

    blocker_uint64 >>= self._np_64 - self.b_magic.shifts[square]

    offset = self.b_offsets[square]

    n_idx = int(offset + blocker_uint64)

    return self.b_attacktables[n_idx]

  #slider attack generation algorithm explained :

  # start from square i. get the innerBB, mask edge values.
  # use chessboards tool to get the list of active idx in the f blocker mask, use utils Combo solver to get the combination
  # generate N unique blocker boards from these combinations
  # for each of those, do the following
  # 1. solve possible attacks
  # 2. Hash it with magictable, shift the bits, insert it in the actual attack table
  # 3. Move the offset 2^Shifts for that square insertions (example, combinations for rook on a1 is 2^12 or something, move offset 2^12

  #rooks = False then fill bishop attack
  def init_sliding_attacks(self, rooks = True) :
    cb = ChessBoard()
    nr_filled = 0

    directions = [[1, 0], [0, -1], [-1, 0], [0, 1]] if rooks else \
      [[1, 1], [1, -1], [-1, 1], [-1, -1]]

    on_board = lambda row, col: row >= 0 and row < 8 and col >= 0 and col < 8
    offset = 0

    _np_one           = np.uint64(1)
    _np_zero          = np.uint64(0)
    _np_64            = np.uint64(64)
    _occupation_mask  = np.uint64(0)
    _sq_to_bb         = np.uint64(0)

    magic_board = RookMagicBitboard() if rooks else BishopMagicBitboard()

    for s_idx in range(64):

      if rooks:
        self.r_offsets.append(int(offset))
      else:
        self.b_offsets.append(int(offset))

      BB_indices = cb.get_pieces_idx_from_uint(magic_board.mask[s_idx])

      for i in range(0, 1 << len(BB_indices)):
        s_64 = np.uint64(i)

        occupation_mask = _np_zero

        for k in range(0, len(BB_indices)):
          if _idx_64[k] & s_64:
            occupation_mask |= _idx_64[BB_indices[k]]

        _sq_to_bb = _np_zero

        for rdir in directions:
          row, col = s_idx//8, s_idx % 8

          while True:
            row += rdir[1]
            col += rdir[0]

            if not on_board(row, col): break

            ns = _idx_64[row*8 + col]

            _sq_to_bb |= ns

            if ns & occupation_mask : break

        # generate hash key and insert
        # we overflow here , somehow doesnt happen in c. i cant figure out how to deal with the problem
        # so i hope to avoid it when i translate this to c later

        occupation_mask *= magic_board.magic_numbers[s_idx]
        occupation_mask >>= _np_64 - magic_board.shifts[s_idx]

        # if occupation_mask > 2 ** (magic_board.shifts[s_idx]):
        #   print("sanity check gone wrong, probably wrong in offset algorithm", occupation_mask, "square id :", s_idx,
        #         "offset : ", offset)

        n_idx = int(offset + occupation_mask)

        if rooks:
          self.r_attacktables[n_idx] = _sq_to_bb
        else:
          self.b_attacktables[n_idx] = _sq_to_bb

        nr_filled += 1

      # move the offset
      offset += 2 ** (magic_board.shifts[s_idx])

    print("{} attack tables initialized. inserted {} attack configs".format('rooks' if rooks else 'bishops', nr_filled))

    if rooks:
      self.rook_init = True
    else:
      self.bishops_init = True



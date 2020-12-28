import numpy as np
from chess_square import Square
from chess_board import ChessBoard

from chess_square import Square, idx_to_row_col, row_col_to_idx
from utils import CombinationSolver

#some help understanding
#https://stackoverflow.com/questions/30680559/how-to-find-magic-bitboards

#the idea is :
#with a given attack table for a square that we call blocker mask
#find all blockers currently occupiying this grid
#we call that blocker board.
#generate a move board from this
#use the magic bitboard algorithm to HASH the blocker board configuration and save a lookup to the move board

class IndexedPawnAttacks :
  def __init__(self):
    self.pawn_attacks = [
      0x0000000000000200, 0x0000000000000500, 0x0000000000000A00,
      0x0000000000001400, 0x0000000000002800, 0x0000000000005000,
      0x000000000000A000, 0x0000000000004000, 0x0000000000020000,
      0x0000000000050000, 0x00000000000A0000, 0x0000000000140000,
      0x0000000000280000, 0x0000000000500000, 0x0000000000A00000,
      0x0000000000400000, 0x0000000002000000, 0x0000000005000000,
      0x000000000A000000, 0x0000000014000000, 0x0000000028000000,
      0x0000000050000000, 0x00000000A0000000, 0x0000000040000000,
      0x0000000200000000, 0x0000000500000000, 0x0000000A00000000,
      0x0000001400000000, 0x0000002800000000, 0x0000005000000000,
      0x000000A000000000, 0x0000004000000000, 0x0000020000000000,
      0x0000050000000000, 0x00000A0000000000, 0x0000140000000000,
      0x0000280000000000, 0x0000500000000000, 0x0000A00000000000,
      0x0000400000000000, 0x0002000000000000, 0x0005000000000000,
      0x000A000000000000, 0x0014000000000000, 0x0028000000000000,
      0x0050000000000000, 0x00A0000000000000, 0x0040000000000000,
      0x0000000000000000, 0x0000000000000000, 0x0000000000000000,
      0x0000000000000000, 0x0000000000000000, 0x0000000000000000,
      0x0000000000000000, 0x0000000000000000, 0x0000000000000000,
      0x0000000000000000, 0x0000000000000000, 0x0000000000000000,
      0x0000000000000000, 0x0000000000000000, 0x0000000000000000,
      0x0000000000000000]

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

    self.knight_attacks = [np.uint64(v) for v in self.knight_attacks] #convert entries to np.uint64

  def __getitem__(self, idx):
    assert idx >= 0 and idx < 64

    return self.knight_attacks[idx]

class BishopMagicBitboard :
  def __init__(self):
    self.magic_numbers = \
    [
      0xc085080200420200,
      0x60014902028010,
      0x401240100c201,
      0x580ca104020080,
      0x8434052000230010,
      0x102080208820420,
      0x2188410410403024,
      0x40120805282800,
      0x4420410888208083,
      0x1049494040560,
      0x6090100400842200,
      0x1000090405002001,
      0x48044030808c409,
      0x20802080384,
      0x2012008401084008,
      0x9741088200826030,
      0x822000400204c100,
      0x14806004248220,
      0x30200101020090,
      0x148150082004004,
      0x6020402112104,
      0x4001000290080d22,
      0x2029100900400,
      0x804203145080880,
      0x60a10048020440,
      0xc08080b20028081,
      0x1009001420c0410,
      0x101004004040002,
      0x1004405014000,
      0x10029a0021005200,
      0x4002308000480800,
      0x301025015004800,
      0x2402304004108200,
      0x480110c802220800,
      0x2004482801300741,
      0x400400820a60200,
      0x410040040040,
      0x2828080020011000,
      0x4008020050040110,
      0x8202022026220089,
      0x204092050200808,
      0x404010802400812,
      0x422002088009040,
      0x180604202002020,
      0x400109008200,
      0x2420042000104,
      0x40902089c008208,
      0x4001021400420100,
      0x484410082009,
      0x2002051108125200,
      0x22e4044108050,
      0x800020880042,
      0xb2020010021204a4,
      0x2442100200802d,
      0x10100401c4040000,
      0x2004a48200c828,
      0x9090082014000,
      0x800008088011040,
      0x4000000a0900b808,
      0x900420000420208,
      0x4040104104,
      0x120208c190820080,
      0x4000102042040840,
      0x8002421001010100
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
    [	0x0080001020400080, 0x0040001000200040, 0x0080081000200080, 0x0080040800100080,
      0x0080020400080080, 0x0080010200040080, 0x0080008001000200, 0x0080002040800100,
      0x0000800020400080, 0x0000400020005000, 0x0000801000200080, 0x0000800800100080,
      0x0000800400080080, 0x0000800200040080, 0x0000800100020080, 0x0000800040800100,
      0x0000208000400080, 0x0000404000201000, 0x0000808010002000, 0x0000808008001000,
      0x0000808004000800, 0x0000808002000400, 0x0000010100020004, 0x0000020000408104,
      0x0000208080004000, 0x0000200040005000, 0x0000100080200080, 0x0000080080100080,
      0x0000040080080080, 0x0000020080040080, 0x0000010080800200, 0x0000800080004100,
      0x0000204000800080, 0x0000200040401000, 0x0000100080802000, 0x0000080080801000,
      0x0000040080800800, 0x0000020080800400, 0x0000020001010004, 0x0000800040800100,
      0x0000204000808000, 0x0000200040008080, 0x0000100020008080, 0x0000080010008080,
      0x0000040008008080, 0x0000020004008080, 0x0000010002008080, 0x0000004081020004,
      0x0000204000800080, 0x0000200040008080, 0x0000100020008080, 0x0000080010008080,
      0x0000040008008080, 0x0000020004008080, 0x0000800100020080, 0x0000800041000080,
      0x00FFFCDDFCED714A, 0x007FFCDDFCED714A, 0x003FFFCDFFD88096, 0x0000040810002101,
      0x0001000204080011, 0x0001000204000801, 0x0001000082000401, 0x0001FFFAABFAD1A2]

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
    self.r_attacktables = np.zeros(shape=(110000), dtype=np.uint64)
    self.b_attacktables = np.zeros(shape=(6000), dtype=np.uint64)
    self.r_offsets = []
    self.b_offsets = []
    self.r_magic = RookMagicBitboard()
    self.b_magic = BishopMagicBitboard()

    self.rook_init = False
    self.bishops_init = False

  def query_rook_attacks(self, square = int, occ = np.uint64):
    assert self.rook_init

    blocker_uint64 = occ & self.r_magic.mask[square]

    blocker_uint64 *= self.r_magic.magic_numbers[square]

    blocker_uint64 >>= np.uint64(64) - self.r_magic.shifts[square]

    offset = int(self.r_offsets[square])

    n_idx = int(offset + blocker_uint64)

    return self.r_attacktables[n_idx]

  def query_bishop_attacks(self, square = Square, occ = np.uint64):
    assert self.bishops_init

    blocker_uint64 = occ & self.b_magic.mask[square]

    blocker_uint64 *= self.b_magic.magic_numbers[square]

    blocker_uint64 >>= np.uint64(64) - self.b_magic.shifts[square]

    offset = int(self.b_offsets[square])

    n_idx = int(offset + blocker_uint64)

    return self.b_attacktables[n_idx]

  #slider attack generation algorithm explained :

  # start from square i. get the innerBB, mask edge values.
  # use chessboards tool to get the list of active idx in the full blocker mask, use utils Combo solver to get the combination
  # generate N unique blocker boards from these combinations
  # for each of those, do the following
  # 1. solve possible attacks
  # 2. Hash it with magictable, shift the bits, insert it in the actual attack table
  # 3. Move the offset 2^Shifts for that square insertions (example, combinations for rook on a1 is 2^12 or something, move offset 2^12

  #rooks = False then fill bishop attack
  def init_sliding_attacks(self, rooks = True):
    cb = ChessBoard()
    nr_filled = 0
    directions = [[1, 0], [0, -1], [-1, 0], [0, 1]] if rooks else \
      [[1,1],[1,-1],[-1,1],[-1,-1]]

    on_board = lambda row, col: row >= 0 and row < 8 and col >= 0 and col < 8
    offset = 0

    magic_board = RookMagicBitboard() if rooks else BishopMagicBitboard()

    for i in range(64):
      _square = Square(i)

      if rooks :
        self.r_offsets.append(offset)
      else :
        self.b_offsets.append(offset)

      BB_indices = cb.get_pieces_idx_from_uint(magic_board.mask[_square.as_int()])

      all_blockerboard_combs = CombinationSolver.get_combinations(BB_indices)
      all_blockerboard_combs.append([]) #add the board where all blocker squares are free

      for blocker_board in all_blockerboard_combs:

        blocker_uint64 = np.uint64(0)

        for bv in blocker_board:
          blocker_uint64 |= np.uint64(1) << np.uint64(bv)

        # now for this blocker board, calculate the legit move , the value we finally will be mapped
        # with this blockerboard
        sq_to_bb = np.uint64(0)
        for rdir in directions:
          row, col = _square.row, _square.col

          while True:
            row += rdir[1]
            col += rdir[0]

            if not on_board(row, col) : break

            ns = Square(row_col_to_idx(row, col)).as_uint64()

            sq_to_bb |= ns

            if (ns & blocker_uint64) != 0: break

        #generate hash key and insert
        blocker_uint64 &= magic_board.mask[_square.as_int()]  # unneccessary?

        blocker_uint64 *= magic_board.magic_numbers[int(_square.as_int())]

        blocker_uint64 >>= np.uint64(64) - magic_board.shifts[_square.as_int()]

        if blocker_uint64 > 2 ** (magic_board.shifts[_square.as_int()]):
          print("sanity check gone wrong, probably wrong in offset algorithm", blocker_uint64, )

        n_idx = int(offset + blocker_uint64)

        if rooks :
          self.r_attacktables[n_idx] = sq_to_bb
        else :
          self.b_attacktables[n_idx] = sq_to_bb

        nr_filled += 1

      # move the offset
      offset += 2 ** (magic_board.shifts[_square.as_int()])

    print("{} attack tables initialized. inserted {} attack configs".format('rooks' if rooks else 'bishops', nr_filled))
    if rooks : self.rook_init = True
    else : self.bishops_init = True




import numpy as np
square_idx_to_uin64t = \
[ np.uint64(1 << v) for v in range(64) ]
square_str_not = \
    [
      'a1',
      'b1',
      'c1',
      'd1',
      'e1',
      'f1',
      'g1',
      'h1',

      'a2',
      'b2',
      'c2',
      'd2',
      'e2',
      'f2',
      'g2',
      'h2',

      'a3',
      'b3',
      'c3',
      'd3',
      'e3',
      'f3',
      'g3',
      'h3',

      'a4',
      'b4',
      'c4',
      'd4',
      'e4',
      'f4',
      'g4',
      'h4',

      'a5',
      'b5',
      'c5',
      'd5',
      'e5',
      'f5',
      'g5',
      'h5',

      'a6',
      'b6',
      'c6',
      'd6',
      'e6',
      'f6',
      'g6',
      'h6',

      'a7',
      'b7',
      'c7',
      'd7',
      'e7',
      'f7',
      'g7',
      'h7',

      'a8',
      'b8',
      'c8',
      'd8',
      'e8',
      'f8',
      'g8',
      'h8'
    ]

class Square :

  def as_int(self):
    return self.idx

  def __init__(self, idx):
    assert idx >= 0 and idx < 64

    self.idx = idx
    self.idx_64 = square_idx_to_uin64t[self.idx]

  def as_uint64(self):
    return self.idx_64

  def __str__(self):
    return square_str_not[self.idx]

  def mirror(self):
    self.idx = 63 - self.idx
    self.idx_64 = square_idx_to_uin64t[self.idx]

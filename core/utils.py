
from copy import deepcopy
import numpy as np

from copy import deepcopy

_np_one = np.uint64(1)
_np_zero = np.uint64(0)
_np_64 = np.uint64(64)

class BinaryHelper :
  def __init__(self):
    pass

  #from an array of integers representing "1" binary values, returns the binary number of all these ones combined
  @staticmethod
  def create_bin_from_int_list(bpos_list = []):
    bv = np.uint64(0)
    for v in bpos_list :
      bv |= np.uint64(1) << np.uint64(v)

    return bv

class CombinationSolver :
  def __init__(self) :
    pass

  @staticmethod
  def get_combinations(arr):
    entries = []
    arr_len = len(arr)

    for i in range(1, arr_len):
      n_arr = deepcopy(arr)
      accum = ''
      CombinationSolver.get_klen_combinations(n_arr, i, accum, entries)

    entries.append(arr)
    return entries

  @staticmethod
  def get_klen_combinations(arr, k, accum='', entries=[]):
    if len(arr) < k: return

    if k == 1:
      for v in arr:
        s = accum + ' ' + str(v)
        vs = s.split(' ')[1:]
        entries.append([int(v_) for v_ in vs])

    elif len(arr) == k:
      for v in arr:
        accum += ' ' + str(v)

      vs = accum.split(' ')[1:]
      entries.append([int(v_) for v_ in vs])

    elif len(arr) > k:
      for i, v in enumerate(arr):
        CombinationSolver.get_klen_combinations(arr[i + 1:], k - 1, accum + ' ' + str(v), entries)

fl_v_0 = np.uint64(0x00000000FFFFFFFF)
fl_v_1 = np.uint64(0xFFFFFFFF00000000)

fl_v_2 = np.uint64(0x0000FFFF0000FFFF)
fl_v_3 = np.uint64(0xFFFF0000FFFF0000)

fl_v_4 = np.uint64(0x00FF00FF00FF00FF)
fl_v_5 = np.uint64(0xFF00FF00FF00FF00)

fl_v_np8 = np.uint64(8)
fl_v_np16 = np.uint64(16)
fl_v_np32 = np.uint64(32)

def flip_vertical(x):
  v = (x & fl_v_0) << fl_v_np32 | (x & fl_v_1) >> fl_v_np32
  v = (v & fl_v_2) << fl_v_np16 | (v & fl_v_3) >> fl_v_np16
  v = (v & fl_v_4) << fl_v_np8  | (v & fl_v_5) >> fl_v_np8
  return v

k1 = np.uint64(0x5555555555555555)
k2 = np.uint64(0x3333333333333333)
k4 = np.uint64(0x0f0f0f0f0f0f0f0f)
#
fl_h_np1 = np.uint64(1)
fl_h_np2 = np.uint64(2)
fl_h_np4 = np.uint64(4)

def flip_horizontal(x):

  v = ((x >> fl_h_np1) & k1) | ((x & k1) << fl_h_np1)
  v = ((v >> fl_h_np2) & k2) | ((v & k2) << fl_h_np2)
  v = ((v >> fl_h_np4) & k4) | ((v & k4) << fl_h_np4)
  return v

board_notations = \
[ "A1","B1","C1","D1","E1","F1","G1","H1",
  "A2","B2","C2","D2","E2","F2","G2","H2",
  "A3","B3","C3","D3","E3","F3","G3","H3",
  "A4","B4","C4","D4","E4","F4","G4","H4",
  "A5","B5","C5","D5","E5","F5","G5","H5",
  "A6","B6","C6","D6","E6","F6","G6","H6",
  "A7","B7","C7","D7","E7","F7","G7","H7",
  "A8","B8","C8","D8","E8","F8","G8","H8"
]


zobrish_prehash = np.zeros(shape=(64,12), dtype=np.uint64)

for square in range(64) :
  for ptype in range(12) :
    zobrish_prehash[square,ptype] = np.uint64(np.random.randint(0, 2**63))



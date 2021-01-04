
from copy import deepcopy
import numpy as np

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

board_notations = \
[
  "A1", "B1","C1","D1","E1","F1","G1","H1",
  "A2", "B2","C2","D2","E2","F2","G2","H2",
  "A3", "B3","C3","D3","E3","F3","G3","H3",
  "A4", "B4","C4","D4","E4","F4","G4","H4",
  "A5", "B5","C5","D5","E5","F5","G5","H5",
  "A6", "B6","C6","D6","E6","F6","G6","H6",
  "A7", "B7","C7","D7","E7","F7","G7","H7",
  "A8", "B8","C8","D8","E8","F8","G8","H8"]


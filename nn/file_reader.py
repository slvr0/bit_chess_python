
import numpy as np

def pop_uint64(intvec) :
  uint64_v = np.uint64(0x0)

  for v in intvec :
    uint64_v |= np.uint64(1) << v

  return v

class TrainingData :
  def __init__(self, board_tensor, logits, logits_idcs, value):
    self.board_tensor = board_tensor
    self.logits = logits
    self.logits_idcs = logits_idcs
    self.value = value

def parse_line_str_to_array(line, as_int = False):
  vs = line.split(' ')
  if as_int :
    return [int(v) for v in vs if v != '\n' and v != '' and v != '&\n']
  else:
    return [float(v) for v in vs if v != '\n' and v != '' and v != '&\n']

def extract_batches(filename):

  board_tensor_ = np.zeros(shape=(13,64))

  batches = []

  with open(filename, mode="r", encoding="utf-8") as f :

    line_count = 0

    while True :
      line = f.readline()
      if not line : break

      # print("vector {} idcs [{}]".format(line_count, line))

      for v in parse_line_str_to_array(line) :

        board_tensor_[line_count, int(v)] = 1

      line_count += 1

      if line_count > 12 :
        line_count = 0
        logits = f.readline()

        nn_idcs = f.readline()
        value = f.readline()

        # print("logits = ", logits)
        # print("nn_idcs = ", nn_idcs)
        # print("value = ", value)

        #populate, reset

        logits_ = parse_line_str_to_array(logits)
        logits_idc_ = parse_line_str_to_array(nn_idcs, as_int = True)
        value = float(value)

        batches.append(TrainingData(board_tensor_, logits_, logits_idc_, value))

        #board_tensor_ = np.zeros(shape=(13, 64))

    print("read {} batches for training, flush file for c script threads to start a new mcts search".format(len(batches)))

    return batches



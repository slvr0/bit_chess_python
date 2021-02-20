
import numpy as np
from nn.actor_critic_network import ActorCriticNetwork

import os
from time import sleep
from core.utils import pseudo_normal_distribution

from nn.data_parser import NN_DataParser
import torch as T
import numpy as np
from time import time

from os import listdir
from os.path import isfile, join


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
    _ = f.readline()
    _ = f.readline()

    line_count = 0

    while True :
      line = f.readline()
      if not line : break

      for v in parse_line_str_to_array(line) :

        board_tensor_[line_count, int(v)] = 1

      line_count += 1

      if line_count > 12 :
        line_count = 0
        logits = f.readline()

        nn_idcs = f.readline()
        value = f.readline()
        _ = f.readline()
        _ = f.readline()

        logits_ = parse_line_str_to_array(logits)
        logits_idc_ = parse_line_str_to_array(nn_idcs, as_int = True)
        value = float(value)

        batches.append(TrainingData(board_tensor_, logits_, logits_idc_, value))

    print("read {} batches for training, flush file for c script threads to start a new mcts search".format(len(batches)))

    return batches

import os
def _read_and_train(num_threads, thread_id, global_network, training_data_path, optimizer, sleep_time = 10,  clip_grad = 0.1) :
  eps_spread = 0.01

  nn_dp = NN_DataParser()

  input_dims = (13,64)
  output_dims  = nn_dp.output_dims

  ac_net = ActorCriticNetwork(input_dim=input_dims, output_dim=output_dims, network_name='ac_localnet_' + str(thread_id))

  ac_net.load_state_dict(global_network.state_dict())

  filename = os.path.join(training_data_path, "thread_{}_data_.txt".format(thread_id))


  save_every = 1000
  entries = 0
  training_loops = 1000

  for i in range(training_loops):

    print("working on training loop nr : {}".format(i))

    #split directory training data based on thread id

    onlyfiles = [f for id, f in enumerate(listdir(training_data_path)) if isfile(join(training_data_path, f))][thread_id::num_threads]

    for file in onlyfiles :
      with open(os.path.join(training_data_path, file), mode="r", encoding="utf-8") as f :
        _ = f.readline()
        _ = f.readline()

        line_count = 0

        while True :
          board_tensor_ = np.zeros(shape=(13, 64))

          line = f.readline()
          if not line : break

          for v in parse_line_str_to_array(line) :
            board_tensor_[line_count, int(v)] = 1

          line_count += 1

          if line_count > 12 :
            line_count = 0
            logits = f.readline()

            nn_idcs = f.readline()
            value = f.readline()
            depth = f.readline()
            visits = f.readline()

            logits_ = parse_line_str_to_array(logits)

            is_white = board_tensor_[12,5]

            if len(logits_) == 0 : continue

            if is_white == 1 : logits_ = pseudo_normal_distribution(logits_)
            else : logits_ = pseudo_normal_distribution(logits_, False)

            m_v = np.max(logits_)

            if (m_v - np.mean(logits_)) < eps_spread : continue

            logits_idc_ = parse_line_str_to_array(nn_idcs, as_int = True)
            value = float(value)

            # print(depth, visits)
            # print(logits_)
            #an entry has been read, train on it
            batch = TrainingData(board_tensor_, logits_, logits_idc_, value)

            board_vec = batch.board_tensor

            branch_idcs = batch.logits_idcs
            value = batch.value

            white_eval = board_vec[12, 5]

            # correction since branch scores are minus for black nodes and we want in range 0 - 1 etc
            if white_eval == 1:
              branch_scores = [1.0 + score for score in batch.logits]
            else:
              branch_scores = [1.0 - score for score in batch.logits]

            if white_eval and value < 0 : value = 0
            elif not white_eval :
              if value > 0 : value = 0
              else : value = abs(value)

            scores_full = np.zeros(shape=output_dims)

            for idx, v in zip(branch_idcs, branch_scores):
              scores_full[idx] = v

            board_vec = board_vec.flatten()
            board_tensor = T.FloatTensor([board_vec])

            net_logits, net_value = ac_net(board_tensor)

            pred_logits = T.FloatTensor([scores_full])

            critic_loss = value - net_value

            probability_ratio = net_logits.exp() / pred_logits.exp()

            weight_prob_ratio_clipped = T.clamp(probability_ratio, 1 - clip_grad, 1 + clip_grad)

            a_loss = T.mean(weight_prob_ratio_clipped[0])
            c_loss = critic_loss[0].item()

            total_loss = a_loss + .5 * c_loss

            optimizer.zero_grad()
            total_loss.backward()

            for local_param, global_param in zip(ac_net.parameters(), global_network.parameters()):
              if global_param.grad is not None:
                break
              global_param._grad = local_param.grad

            optimizer.step()
            entries += 1

            if(entries % save_every == 0) :
              print("{} Entries processed on thread {} , saving net...".format(entries, thread_id))

  global_network.save_network()








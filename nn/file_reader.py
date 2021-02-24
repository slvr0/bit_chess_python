
import numpy as np
from nn.actor_critic_network import ActorCriticNetwork

import os
from time import sleep
from core.utils import pseudo_normal_distribution

from torch.nn import MSELoss
import torch.nn.functional as F

from nn.data_parser import NN_DataParser
import torch as T
import numpy as np
from time import time

from torch.utils.tensorboard import *


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


def _read_and_train(num_threads, thread_id, global_network, training_data_path, optimizer, sleep_time = 10,  clip_grad = 0.1) :

  if thread_id == 0 :
    tensorboard = SummaryWriter('logs', flush_secs=10)

  eps_spread = 0.01

  nn_dp = NN_DataParser()

  input_dims = (13,64)
  output_dims  = nn_dp.output_dims

  ac_net = ActorCriticNetwork(input_dim=input_dims, output_dim=output_dims, network_name='ac_localnet_' + str(thread_id))

  ac_net.load_state_dict(global_network.state_dict())

  save_every = 1000
  entries = 0
  training_loops = 100000

  iteration_idx  = 0
  for i in range(training_loops):

    print("working on training loop nr : {}".format(i))

    onlyfiles = [f for id, f in enumerate(listdir(training_data_path)) if isfile(join(training_data_path, f))][
                thread_id::num_threads]

    for file_idx, file in enumerate(onlyfiles) :

      ac_net.load_state_dict(global_network.state_dict())

      with open(os.path.join(training_data_path, file), mode="r", encoding="utf-8") as f :

        _ = f.readline()
        _ = f.readline()

        line_count = 0

        board_tensor_ = np.zeros(shape=(1, 1, 13, 64))

        while True :

          line = f.readline()
          if not line : break

          for v in parse_line_str_to_array(line) :
            board_tensor_[0,0,line_count, int(v)] = 1

          line_count += 1

          if line_count > 12 :

            line_count = 0
            logits = f.readline()

            nn_idcs = f.readline()
            value = f.readline()
            depth = f.readline()
            visits = f.readline()

            logits_ = parse_line_str_to_array(logits)

        is_white = board_tensor_[0,0,12,5]

        if len(logits_) == 0 : continue

        if is_white == 1 : logits_ = pseudo_normal_distribution(logits_)
        else : logits_ = pseudo_normal_distribution(logits_, False)

        m_v = np.max(logits_)

        if (m_v - np.mean(logits_)) < eps_spread : continue

        logits_idc_ = parse_line_str_to_array(nn_idcs, as_int = True)
        value = float(value)

        batch = TrainingData(board_tensor_, logits_, logits_idc_, value)

        board_vec = batch.board_tensor

        value = batch.value

        #correct value function for white/node position
        #logits value are automaitically corrected in the pseudo distribution fucntion
        white_eval = board_vec[0, 0, 12, 5]
        if white_eval and value < 0:
          value = 0
        elif not white_eval:
          if value > 0:
            value = 0
          else:
            value = abs(value)

        #board_vec = board_vec.flatten()
        board_tensor = T.FloatTensor(board_vec)

        simul_logits_full = np.zeros(shape=(output_dims))

        # batch.logits = n values, net_logits = N (output dim) values
        for idx, v in zip(batch.logits_idcs, batch.logits):
          simul_logits_full[idx] = v

        simul_logits_full = T.FloatTensor([simul_logits_full])

        for i in range(1) :

          iteration_idx += 1

          net_logits, net_value = ac_net(board_tensor)


          net_logits = F.softmax(net_logits, dim=0)

          critic_loss = value - net_value

          criterion = MSELoss()
          #a_loss = criterion(net_logits[0, :], simul_logits_full[0, :])

          #print(a_loss)
          #probability_ratio = net_logits.exp() / simul_logits_full.exp()

          a_loss = criterion(net_logits[0], simul_logits_full[0]) * 100.0

          #a_loss = T.clamp(a_loss, 1 - clip_grad, 1 + clip_grad)

          #print(a_loss)
          # weight_prob_ratio_clipped = T.clamp(probability_ratio, 1 - clip_grad, 1 + clip_grad)
          #
          # a_loss = T.mean(weight_prob_ratio_clipped[0])
          #
          # c_loss = critic_loss[0].item()

          #print(weight_prob_ratio_clipped)

          total_loss = a_loss

          # print(a_loss, total_loss)

          optimizer.zero_grad()
          total_loss.backward()

          if thread_id == 0 :
            #log on thread 0
            tensorboard.add_scalar('total_loss', total_loss, iteration_idx)
            #tensorboard.add_scalar('actor_loss', a_loss, iteration_idx)
            #tensorboard.add_scalar('critic_loss', c_loss , iteration_idx)

          for local_param, global_param in zip(ac_net.parameters(), global_network.parameters()):
            if global_param.grad is not None:
              break
            global_param._grad = local_param.grad

          optimizer.step()
          entries += 1

        if(entries % save_every == 0) :
          print("{} Entries processed on thread {} , saving net...".format(entries, thread_id))
          global_network.save_network()

  global_network.save_network()








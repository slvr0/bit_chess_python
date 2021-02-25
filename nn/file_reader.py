
import numpy as np
from nn.actor_critic_network import ActorCriticNetwork

import os
from time import sleep
from core.utils import pseudo_normal_distribution
from nn.keras_net import KerasNet

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

class BatchCollector :
  def __init__(self, root_folder, on_thread, num_threads):
    self.root_folder = root_folder
    self.on_thread = on_thread
    self.num_threads = num_threads
    self.batches = []

  def read_entry(self, filename):
    with open(os.path.join(self.root_folder, filename), mode="r", encoding="utf-8") as f:

      d = f.readline()
      v = f.readline()

      line_count = 0

      board_tensor = np.zeros(shape=(13, 64))

      while True:

        line = f.readline()
        if not line: break

        for v in parse_line_str_to_array(line):
          board_tensor[line_count, int(v)] = 1

        line_count += 1

        if line_count > 12:
          line_count = 0
          logits = f.readline()

          nn_idcs = f.readline()
          logits_idc_ = parse_line_str_to_array(nn_idcs, as_int=True)

          value = f.readline()

          #depth = f.readline() #not used atm
          #visits = f.readline() #not used atm

          logits = parse_line_str_to_array(logits)

      #print(d,v)
      data = TrainingData(board_tensor, logits, logits_idc_, value)

      # if filename == "file_1613775792907.txt" :
      #   parser = NN_DataParser()
      #   parser.decode_training_batch(data)

      return data

  def preprocess_batch(self, batch, eps_spread = 0.01):
    is_white = batch.board_tensor[12, 5]

    if len(batch.logits) == 0 : return batch, False

    if is_white == 1:
      batch.logits = pseudo_normal_distribution(batch.logits)
    else:
      batch.logits = pseudo_normal_distribution(batch.logits, False)

    m_v = np.max(batch.logits)

    if (m_v - np.mean(batch.logits)) < eps_spread: return batch, False

    batch.value = float(batch.value)

    white_eval = batch.board_tensor[12, 5]
    if white_eval and batch.value < 0:
      batch.value = 0
    elif not white_eval:
      if batch.value > 0:
        batch.value = 0
      else:
        batch.value = abs(batch.value)

    return batch, True

  def collect_batches(self, preprocess = True):
    self.reset_collection()

    #f0 = file_1613775792907
    onlyfiles = [f for id, f in enumerate(listdir(self.root_folder)) if isfile(join(self.root_folder, f))][
                self.on_thread::self.num_threads]

    for file_idx, file in enumerate(onlyfiles) :
      batch = self.read_entry(file)

      if preprocess :
        prep_batch, success_preprocess = self.preprocess_batch(batch)
        if success_preprocess : self.batches.append(prep_batch)

      else : self.batches.append(batch)

  def parse_for_training(self):
    #training only want pure tensor input and output logits

    inputs = np.ndarray( shape=(len(self.batches), 13*64))
    outputs = np.ndarray( shape=(len(self.batches), 1879))

    for idx, batch in enumerate(self.batches) :
      output = np.zeros(shape=1879)
      for i, v in zip(batch.logits_idcs, batch.logits): output[i] = v

      inputs[idx] = batch.board_tensor.flatten()
      outputs[idx] = output

    return  inputs, outputs

  def reset_collection(self):
    self.batches = []

def _read_and_train(num_threads, thread_id, global_network, training_data_path, optimizer, sleep_time = 10,  clip_grad = 0.1) :

  epochs = 10000

  logger = SummaryWriter('logs')

  save_every = 100

  nn_dp = NN_DataParser()

  input_dims = 13*64
  output_dims = nn_dp.output_dims

  net = KerasNet(input_dims, output_dims, 'net_'+ str(thread_id))

  net.load_model()

  batch_collector = BatchCollector(training_data_path, thread_id, num_threads)

  batch_collector.reset_collection()

  batch_collector.collect_batches(preprocess=True)

  inputs, outputs  = batch_collector.parse_for_training()

  entries = len(inputs)
  #split for training testing

  train_data = inputs[:int(entries*.6)]
  train_output = outputs[:int(entries*.6)]

  test_data = inputs[int(entries*.6):]
  test_output = outputs[int(entries*.6):]

  for epoch in range(epochs) :
    net.train_on_batch(train_data, train_output)
    loss = net.test_on_batch(test_data, test_output)

    logger.add_scalar('loss_{}'.format(thread_id) , loss, epoch)

    if(epoch % save_every == 0 ) :
      #print("checkpoint reached, saving net")
      net.save_model()










##constantly read from training data dirr, if data is there collect it and send for training

from nn.actor_critic_network import ActorCriticNetwork

import os
from time import sleep
from nn.file_reader import extract_batches
from nn.data_parser import NN_DataParser
import torch as T
import numpy as np
from time import time
#training data structure
# class TrainingData :
#   def __init__(self, board_tensor, logits, logits_idcs, value):
#     self.board_tensor = board_tensor (np array (13,64)
#     self.logits = logits (N) N = branches
#     self.logits_idcs = logits_idcs (N)
#     self.value = value (1)

#batches = array(TrainingData)

def _batch_collect_on_thread(thread_id, global_network, training_data_path, optimizer, sleep_time = 10,  clip_grad = 0.1) :

  nn_dp = NN_DataParser()

  input_dims = (13,64)
  output_dims  = nn_dp.output_dims

  ac_net = ActorCriticNetwork(input_dim=input_dims, output_dim=output_dims, network_name='ac_localnet_0')

  ac_net.load_state_dict(global_network.state_dict())

  data_path = os.path.join(training_data_path, "thread_{}_data.txt".format(thread_id))

  while True :
    if not os.path.isfile(data_path) :
      sleep(sleep_time)
    else :
      print("thread[{}] initiated".format(thread_id))
      sleep(sleep_time)
      batches = extract_batches(data_path)
      # try :
      #   os.remove(data_path)
      # except:
      #   print("error removing file after collecting batches")

      start_time = time()

      progress_bar_inc = int((len(batches)) / 100.0)
      progress_bar = 0

      progress_bar_percent = 0

      for idc, batch in enumerate(batches) :

        if idc > progress_bar :
          progress_bar_percent += 1
          progress_bar += progress_bar_inc
          print("thread[{}] training status[ {}% ]".format(thread_id, progress_bar_percent))

        board_vec = batch.board_tensor

        branch_idcs = batch.logits_idcs
        value = batch.value

        white_eval = board_vec[12,5]

        #correction since branch scores are minus for black nodes and we want in range 0 - 1 etc
        if white_eval == 1 :
          branch_scores = [1.0 + score for score in batch.logits]
        else :
          branch_scores = [1.0 - score for score in batch.logits]

        value = abs(value)

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

      print("Training batch completed on thread {}, {} entries analyzed, sleeping waiting for new batch".format(thread_id, len(batches)))
      end_time = time()
      print('The code runs for %.2f s ' % (end_time - start_time))
      global_network.save_network()



























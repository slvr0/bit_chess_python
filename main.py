
### IMPORTANT
### The focus on this code is to use test cases to satisify that all logic is working correct!

# scrapboard structure
# board consist of a uint64_t for each piece type, the ones represent position of each piece
# ex. our_pawns, our_knights, our_bishops, our_rooks, our_queens, our_king
# and enemy_pawns, etc...

# board will have following functionality :
# debug, printout in console mod aswell as genering a fen string line,
# queering legal moves , returning a list of possible actions (not handling serialization of those, deal with it somewhere else)
# flipping the board , and thereby storing what side is currently acting on it (white/black = 1/0)

#well start with this, seems hard enough. queering legal moves is later prio ( we want attack tables generated first )

#future  :
#board serializer : takes in a chessboard and outputs 12 tensors (for each piece type )
#castling class, takes care of castling rights and check if possible in current state
#repetion class, checks 50 move rule, threefold repetition
#attack tables, caching all possible attacks with magic bitboard combinations
#boardplay wrapper, a class that wraps logic so user can simply play a game without touching logic
#for example, class with step taking a chess action input and outputs if game is over, next gameboard state and reward(reward is = 1 for winner etc.)
#network preparation, pytorch net with agent
#the memory and its algorithm, playing games will result in millions of positions, it will be too broad action space,
#have to be limited , learn about monte carlo search tree to optimize the training data

from test.run_tests import _run_tests
from test.random_chessplay_test import run_test
from test.move_generator_test import run_move_generator_test
from core.move_generator import MoveGenerator

from mcts.cached_mcts_positions import CachedMCTSPositions
from nn.NNMCTSPipe import NNMCTSPipe

from time import time
import numpy as np
import ctypes
from core.chess_square import idx_to_row_col
from copy import deepcopy
from core.chess_board import ChessBoard

from test.mcts_test import run_mcts_test
from core.chess_square import _idx_64
from wrappers.chess_env import ChessEnvironment

import multiprocessing as mp

import threading

from core.utils import pseudo_normal_distribution
import numpy as np
from nn.data_parser import NN_DataParser

from nn.file_reader import _read_and_train
from nn.auto_batch_collect import _batch_collect_on_thread
from nn.actor_critic_network import ActorCriticNetwork
from nn.shared_optim import GlobalAdam
import torch as T
import torch.multiprocessing as torch_mp
from nn.network_eval import test
from simul.chess_gui import init_gui_env
from simul.non_gui_simul import NonGUISimulationEnvironment

from communication.nn_mqtt_requester import NN_MQTT_Requester, nn_mqtt_req_on_thread
import threading

def start_training_environment() :

    nn_dp = NN_DataParser()

    input_dims = (13, 64)
    output_dims = nn_dp.output_dims

    global_net = ActorCriticNetwork(input_dim=input_dims, output_dim=output_dims, network_name='ac_global')

    optimizer = GlobalAdam(global_net.parameters(), lr=1e-3)
    sleep_time = 10
    clip_grad = .1
    n_threads = 1

    mp = torch_mp.get_context("spawn")

    processes = []

    for index in range(n_threads):
        process = mp.Process(target=_read_and_train,
                             args=(
                             n_threads, index, global_net, "/home/dan/build-bitchess_2-Desktop-Debug/training_data", optimizer,
                             sleep_time, clip_grad))

        process.start()
        processes.append(process)

    for process in processes:
        process.join()

def start_nongui_simulation(start_pos) :
    from communication.mqtt_comm import Subscriber
    from communication.nn_mqtt_requester import NN_MQTT_Requester
    from mcts.cached_mcts_positions import CachedMCTSPositions

    cached_positions = CachedMCTSPositions()

    move_gen = MoveGenerator()

    #non_gui_sim_env = NonGUISimulationEnvironment(on_thread=True)

    #start from this position outside
    cb = ChessBoard(start_pos)

    mp = torch_mp.get_context("spawn")

    processes = []

    process = mp.Process(target=nn_mqtt_req_on_thread, args=('mcts_nn_que', 'mcts_cache_position', move_gen))

    process.start()
    processes.append(process)

    process = mp.Process(target= NonGUISimulationEnvironment.start_game,
                         args=(cb, move_gen, cached_positions,  0, True))

    process.start()
    processes.append(process)

    for process in processes:
        process.join()

    #non_gui_sim_env.start_game(cb, 0)

def start_tests() :
    move_gen = MoveGenerator()
    _run_tests(None, move_gen)

import torch as T
import torch.nn.functional as F
import torch.nn as nn
import os

from torch import sigmoid, optim

from nn.actor_critic_network import ActorCriticNetwork

def test_mqtt_env() :
    from communication.mqtt_comm import Subscriber
    mqtt_sub = Subscriber("mqtt_test")



    #
    # mqtt_sub.connect("localhost")
    # mqtt_sub.subscribe("mqtt_test")
    #
    # mqtt_sub.loop_forever()

    # import paho.mqtt.client as mqtt
    # def on_connect(client, userdata, flags, rc):
    #     print("Connected with result code " + str(rc))
    # def on_message(client, userdata, msg):
    #     print(msg.topic + " " + str(msg.payload))
    # client = mqtt.Client()
    # client.on_connect = on_connect
    # client.on_message = on_message
    # client.connect("localhost", 1883, 60)
    # client.subscribe("mqtt_test")
    # client.loop_forever()

if __name__ == '__main__':

    #test_mqtt_env()

    #start_training_environment()

    start_nongui_simulation("rnbqk1nr/ppp2ppp/4p3/3p4/1b1PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 2 4")

    #self.client.publish('mcts_cache_position', msg.payload)


    # msg = "2rq2k1/pprbbpp1/4pn1p/3pN3/3B4/1N2P3/P1n1BPPP/RQ3RK1 w - - 10 20"
    # #add net eval of position
    #
    # move_gen = MoveGenerator()
    # nn_parser = NN_DataParser()
    #
    # from nn.keras_net import KerasNet
    #
    # input_dim = (13, 64)
    # output_dim = nn_parser.output_dims
    #
    # ac_net = KerasNet(13 * 64, output_dim, 'net_0')
    # graph = ac_net.load_model(on_thread=False)
    #
    # cb = ChessBoard(msg)
    #
    # actions = move_gen.get_legal_moves(cb)
    #
    # nn_idcs = [nn_parser.nn_move(m) for m in actions]
    #
    # tensor_data = nn_parser.nn_board(cb)
    #
    # net_logs = ac_net.predict(tensor_data.flatten())
    #
    # net_logs = [v for i,v in enumerate(net_logs[0]) if i in nn_idcs]
    #
    # msg += " {"
    # for idx, log in zip(nn_idcs, net_logs) :
    #
    #     msg += "{0}:{1:1f}:".format(int(idx),log)
    # msg = msg[:-1] + "}"














































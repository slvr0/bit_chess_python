
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
from nn.file_reader import extract_batches
from nn.file_reader import _read_and_train
from nn.auto_batch_collect import _batch_collect_on_thread
from nn.actor_critic_network import ActorCriticNetwork
from nn.shared_optim import GlobalAdam
import torch as T
import torch.multiprocessing as torch_mp
from nn.network_eval import test
from simul.chess_gui import init_gui_env
from simul.non_gui_simul import NonGUISimulationEnvironment

def start_training_environment() :
    nn_dp = NN_DataParser()

    input_dims = (13, 64)
    output_dims = nn_dp.output_dims

    global_net = ActorCriticNetwork(input_dim=input_dims, output_dim=output_dims, network_name='ac_global')

    optimizer = GlobalAdam(global_net.parameters(), lr=1e-4)
    sleep_time = 10
    clip_grad = .1
    n_threads = 5

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
    non_gui_sim_env = NonGUISimulationEnvironment()

    #start from this position outside
    cb = ChessBoard(start_pos)

    non_gui_sim_env.start_game(cb, 0)

def start_tests() :
    move_gen = MoveGenerator()
    _run_tests(None, move_gen)


if __name__ == '__main__':

    start_nongui_simulation("rnbqk1nr/ppp2ppp/4p3/3p4/1b1PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 2 4")

    #start_training_environment()



























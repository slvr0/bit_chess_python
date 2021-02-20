
import torch as T

from core.chess_board import ChessBoard
from core.move_generator import MoveGenerator
from nn.data_parser import *
from nn.actor_critic_network import ActorCriticNetwork
import torch.nn.functional as F
from nn.data_parser import NN_DataParser
from core.move_generator import MoveGenerator

#first network eval
def test(move_gen):
  T.manual_seed(123)

  parser = NN_DataParser()
  input_dims = (13*64)
  output_dims =  parser.output_dims

  model = ActorCriticNetwork(input_dims, output_dims,'ac_global')
  model.load_network()

  model.eval()

  positions = [
        "rnbqk2r/pp1p1pbp/2p2np1/4p3/2P5/2N1P1P1/PP1P1PBP/R1BQK1NR w KQkq - 0 6", #//english std
        "rr1q3k/2bnn2p/3pp3/5pp1/2PPP3/2BNP1P1/1P1QRPBP/1R4K1 w q - 0 1",
        "8/8/3R4/5PP1/4NN2/5K2/8/r4k2 w - - 0 1",
        "4k2b/2b2q2/1nn1p3/4P3/6p1/P2PN2p/2Q1N1PP/R2K2P1 w Q - 0 1",
        "rnbqk1nr/ppp2ppp/4p3/3p4/1b1PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 2 4", #//french winaware
        "r1bqkbnr/2pp1ppp/p1n5/1p2p3/B3P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 5", #//ruy lopz
        "r1bqk2r/pp1n1ppp/2p1pn2/8/1bpP4/2N2NP1/PP2PPBP/R1BQ1RK1 w kq - 0 8", #//catalan/slav exchange
        "rnbqk2r/ppp1ppbp/3p1np1/8/2PPP3/2N5/PP3PPP/R1BQKBNR w KQkq - 0 5", #//kings indian
        "rnbqkbnr/pppp1ppp/8/4P3/8/8/PPP1PPPP/RNBQKBNR b KQkq - 0 2",# //englund gambit
        "r1bqk2r/ppp2ppp/2p2n2/2b5/4P3/2N5/PPPP1PPP/R1BQKB1R w KQkq - 2 6"#//stafford
  ]
  for position in positions :
    cb = ChessBoard(position)

    board_vec = parser.nn_board(cb)

    board_vec = board_vec.flatten()
    board_tensor = T.FloatTensor([board_vec])

    net_logits, net_value = model(board_tensor)

    moves = move_gen.get_legal_moves(cb)

    nn_move_dict_translate = dict()

    legal_idcs = []
    for midx, move in enumerate(moves) :
      nn_idx = parser.nn_move(move)

      nn_move_dict_translate[nn_idx] = midx
      legal_idcs.append(nn_idx)

    for i in range(parser.output_dims):
      if i not in legal_idcs :
        net_logits[0][i] = 0.0

    policy = F.softmax(net_logits, dim=1)
    action = T.argmax(policy).item()

    optim_move_idx = nn_move_dict_translate[action]
    moves[optim_move_idx].print_move()

    #cb.print_console()

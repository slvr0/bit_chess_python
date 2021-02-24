import torch as T
import torch.nn.functional as F
import torch.nn as nn
import os

from torch import sigmoid, optim

class ActorCriticNetwork(nn.Module):
    def __init__(self, input_dim, output_dim, network_name):
        super(ActorCriticNetwork, self).__init__()

        self.chkpt_dir = os.path.join('nn/nn_models', str(network_name))

        #self.fc1 = nn.Linear(8 * 8 * 13, 320)  # 8*8 board, 12 piece types
        # self.fc1 = nn.Linear(8 * 8 * 13, 208)  # 8*8 board, 12 piece types
        # self.fc2 = nn.Linear(208, 84)
        #
        # self.critic_linear = nn.Linear(84, 1)
        # self.actor_linear = nn.Linear(84, output_dim)

        self.conv1 = nn.Conv2d(1, 64, 3, stride=2, padding=1)
        self.conv2 = nn.Conv2d(64, 32, 3, stride=2, padding=1)
        # self.conv3 = nn.Conv2d(32, 32, 3, stride=2, padding=1)
        # self.conv4 = nn.Conv2d(32, 32, 3, stride=2, padding=1)

        self.critic_linear = nn.Linear(2048, 1)
        self.actor_linear = nn.Linear(2048, output_dim)

        self._initialize_weights()

    def _initialize_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Conv2d) or isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.LSTMCell):
                nn.init.constant_(module.bias_ih, 0)
                nn.init.constant_(module.bias_hh, 0)

    def forward(self, x):

        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))

        x = T.flatten(x)

        return self.actor_linear(x), self.critic_linear(x)

    def save_network(self):
        print("saving network...")
        T.save(self.state_dict(), self.chkpt_dir)

    def load_network(self):
        if os.path.isfile(self.chkpt_dir):
            print("loading network")
            self.load_state_dict(T.load(self.chkpt_dir))
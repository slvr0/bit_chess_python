
import torch as T

class GlobalAdam(T.optim.Adam):
  def __init__(self, params, lr):
    super(GlobalAdam, self).__init__(params, lr=lr)
    for group in self.param_groups:
      for p in group['params']:
        state = self.state[p]
        state['step'] = 0
        state['exp_avg'] = T.zeros_like(p.data)
        state['exp_avg_sq'] = T.zeros_like(p.data)

        state['exp_avg'].share_memory_()
        state['exp_avg_sq'].share_memory_()

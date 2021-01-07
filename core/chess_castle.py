
import numpy as np

class Castling :
  def __init__(self):
    self.we_can_00 = True
    self.we_can_000 = True
    self.enemy_can_00 = True
    self.enemy_can_000 = True

    self.castle_info_serialized = np.uint16(0xFFFF)

  def reset(self) :
    self.we_can_00 = True
    self.we_can_000 = True
    self.enemy_can_00 = True
    self.enemy_can_000 = True

    self.castle_info_serialized = np.uint16(0xFFFF)

  def update_castlestatus(self, chessmove):
    pt = chessmove.ptype
    if pt == 'K' :
      self.set_we_00(False)
      self.set_we_000(False)
      return

    if pt == 'R' :
      if chessmove._from == 0 :
        self.set_we_000(False)
      elif chessmove._from == 7 :
        self.set_we_00(False)

    if chessmove.to == 63 :
      self.set_enemy_00(False)
    if  chessmove.to == 56 :
      self.set_we_000(False)

  def as_serialized(self):
    return self.castle_info_serialized

  def set_we_00(self, _opt = True):
    self.we_can_00 = _opt

  def set_we_000(self, _opt = True):
    self.we_can_000 = _opt

  def set_enemy_00(self, _opt = True):
    self.enemy_can_00 = _opt

  def set_enemy_000(self, _opt = True):
    self.enemy_can_000 = _opt

  def we_00(self):
    return self.we_can_00

  def we_000(self):
    return self.we_can_000

  def enemy_00(self):
    return self.enemy_can_00

  def enemy_000(self):
    return self.enemy_can_000

  def mirror(self):
    w_00 = self.we_can_00
    w_000 = self.we_can_000

    self.we_can_00 = self.enemy_can_00
    self.we_can_000 = self.enemy_can_000

    self.enemy_can_00 = w_00
    self.enemy_can_000 = w_000


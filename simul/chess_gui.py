import PyQt5 as qt

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import QPoint, QRect, QEvent, QEventLoop
from PyQt5.QtWidgets import QWidget, QAction, QLabel, QLayoutItem
from PyQt5.QtGui import QCursor

import os
import sys
import numpy as np

from simul import logic
#taken from the board pixels img

psize = 60

mw_size_x = 695
mw_size_y = 720

bsq_w = int(mw_size_x/8)
bsq_h = int(mw_size_y/8)

board_geom_xy = np.zeros(shape=(64,2) , dtype=np.int)

class CustomQAction(QtWidgets.QAction) :

  clicked_sq = -1

  def __init__(self, parent = None):
    super(CustomQAction, self).__init__(parent)

for r in range(8) :
  for c in range(8) :
    board_geom_xy[c + (8 * r), 0] = c * bsq_w
    board_geom_xy[c + (8 * r), 1] = (7 - r) * bsq_h #reversing y coord here to fit board

def init_gui_env() :
  app = QtWidgets.QApplication(sys.argv)

  board_view = GUI_ChessBoard()

  main_window = GUI_MainWindow(board_view)

  main_window.show()

  sys.exit(app.exec_())


class GUI_ChessBoard(QtWidgets.QWidget) :

  def __init__(self):

    super(GUI_ChessBoard, self).__init__()

    self.piece_selected = False
    self.piece_selected_at = -1

    self.label = QtWidgets.QLabel()

    self.label.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/chessboard2.png"))

    self.qact_select = CustomQAction(self)

    self.qact_select.triggered.connect(self.select_callback)

    self.ghost_piece = None

    self.logic = logic.GUI_Logic()

    self.pieces = \
    [
    GUI_ChessPiece(0, 'R', self.qact_select, self),
    GUI_ChessPiece(1, 'N', self.qact_select, self),
    GUI_ChessPiece(2, 'B', self.qact_select, self),
    GUI_ChessPiece(3, 'Q', self.qact_select, self),
    GUI_ChessPiece(4, 'K', self.qact_select, self),
    GUI_ChessPiece(5, 'B', self.qact_select, self),
    GUI_ChessPiece(6, 'N', self.qact_select, self),
    GUI_ChessPiece(7, 'R', self.qact_select, self),
    GUI_ChessPiece(8, 'P', self.qact_select, self),
    GUI_ChessPiece(9, 'P', self.qact_select, self),
    GUI_ChessPiece(10, 'P', self.qact_select, self),
    GUI_ChessPiece(11, 'P', self.qact_select, self),
    GUI_ChessPiece(12, 'P', self.qact_select, self),
    GUI_ChessPiece(13, 'P', self.qact_select, self),
    GUI_ChessPiece(14, 'P', self.qact_select, self),
    GUI_ChessPiece(15, 'P', self.qact_select, self),

    GUI_ChessPiece(48, 'p', self.qact_select, self),
    GUI_ChessPiece(49, 'p', self.qact_select, self),
    GUI_ChessPiece(50, 'p', self.qact_select, self),
    GUI_ChessPiece(51, 'p', self.qact_select, self),
    GUI_ChessPiece(52, 'p', self.qact_select, self),
    GUI_ChessPiece(53, 'p', self.qact_select, self),
    GUI_ChessPiece(54, 'p', self.qact_select, self),
    GUI_ChessPiece(55, 'p', self.qact_select, self),

    GUI_ChessPiece(56, 'r', self.qact_select, self),
    GUI_ChessPiece(57, 'n', self.qact_select, self),
    GUI_ChessPiece(58, 'b', self.qact_select, self),
    GUI_ChessPiece(59, 'q', self.qact_select, self),
    GUI_ChessPiece(60, 'k', self.qact_select, self),
    GUI_ChessPiece(61, 'b', self.qact_select, self),
    GUI_ChessPiece(62, 'n', self.qact_select, self),
    GUI_ChessPiece(63, 'r', self.qact_select, self)
    ]

    for i in range(16, 48) :
      self.pieces.append(GUI_ChessPiece(i, '', self.qact_select, self))

    self.flip()
    self.flip(True)

  def swap_pieces(self, _from, _to):

    self.pieces[_to]._set_type(self.pieces[_from].type)
    self.pieces[_from]._set_type('')

    #self.pieces.append(GUI_ChessPiece(_from, '', self.qact_select, self))

  def select_callback(self):
    if self.piece_selected :
      self.piece_selected = False

      nsq = self.qact_select.last_trigger_sq
      osq = self.piece_selected_at

      osq_idx = -1
      nsq_idx = -1

      for idx, piece in enumerate(self.pieces) :
        if piece.sq == osq : osq_idx = idx
        elif piece.sq == nsq : nsq_idx = idx

      if osq_idx == nsq_idx or osq_idx < 0 or osq_idx >= 64 or nsq_idx < 0 or osq_idx >= 64: return

      is_legal = self.logic.query_legal_move(osq, nsq)

      if not is_legal : return

      self.swap_pieces(osq_idx, nsq_idx)

      #now directly que a move for computer
      _from, to = self.logic.query_computer_move()

      _from = 63 - _from
      to = 63 - to

      osq_idx = -1
      nsq_idx = -1

      for idx, piece in enumerate(self.pieces) :
        if piece.sq == _from : osq_idx = idx
        elif piece.sq == to : nsq_idx = idx

      self.swap_pieces(osq_idx, nsq_idx)

    else :
      self.piece_selected_at = self.qact_select.last_trigger_sq
      self.piece_selected = True

  def flip(self, fblack = False):
    for piece in self.pieces :
      piece._flip(fblack)
    # for key in self.pieces :
    #   self.pieces[key]._flip(fblack)

  def _setup_pieces(self, fen = ""):
    pawn = GUI_ChessPiece(8, 'P')
    self.grid.addWidget(pawn, 1, 1)

    self.pieces[8] = pawn

class GUI_ChessPiece(QtWidgets.QLabel) :
  def __init__(self, sq, type, select_action, parent=None):
    super(GUI_ChessPiece, self).__init__()
    self.sq = sq
    self.type = type
    self.selected = False
    self.setParent(parent)
    self.select_action = select_action
    self._set_lb()
    self._set_pos()

  def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
    self.select_action.last_trigger_sq = self.sq
    self.select_action.trigger()

    self.selected = True

  def _delete_widget(self):
    self.deleteLater()

  def _set_sq(self, sq ):
    self.sq = sq
    self._set_pos()

  def _flip(self, fblack=False):
    self.sq = 63 - self.sq
    self._set_pos()

  def _set_pos(self):
    self.setGeometry(QtCore.QRect(*board_geom_xy[self.sq], 60 , 60))

  def _set_type(self, type):
    self.type = type

    self._set_lb()

  def _set_lb(self):
    #can be set to blank aswell
    if self.type == 'P' : self.setPixmap(QtGui.QPixmap(os.getcwd()   + "/simul/media/Chess_plt60.png"))
    elif self.type == 'N' : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_nlt60.png"))
    elif self.type == 'B' : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_blt60.png"))
    elif self.type == 'R' : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_rlt60.png"))
    elif self.type == 'Q' : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_qlt60.png"))

    elif self.type == 'K' : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_klt60.png"))
    elif self.type == 'p':  self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_pdt60.png"))
    elif self.type == 'n' : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_ndt60.png"))
    elif self.type == 'b' : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_bdt60.png"))
    elif self.type == 'r' : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_rdt60.png"))
    elif self.type == 'q' : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_qdt60.png"))
    elif self.type == 'k' : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/Chess_kdt60.png"))
    else : self.setPixmap(QtGui.QPixmap(os.getcwd() + "/simul/media/transp.png"))

class GUI_MainWindow(QtWidgets.QMainWindow) :
  def __init__(self, view):
    super(GUI_MainWindow, self).__init__()

    img = QtGui.QImage(QtGui.QPixmap(os.getcwd() + "/simul/media/chessboard2.png"))
    palette = QtGui.QPalette()
    palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(img))
    self.setPalette(palette)

    layout = QtWidgets.QHBoxLayout()

    self.view = view

    layout.addWidget(self.view)

    self.widget = QtWidgets.QWidget()
    self.widget.setLayout(layout)

    self.setCentralWidget(self.widget)
    self.setWindowTitle("Chess Net Test")

    self.setGeometry(600, 100, mw_size_x, mw_size_y)

    self.setFixedSize(mw_size_x, mw_size_y)

    # self.createActions()
    # self.createMenus()
    # self.createDocks()




class GUI_PromotionWindow :
  def __init__(self):
    pass



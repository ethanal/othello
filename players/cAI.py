from . import Player
from ctypes import *
import sys
import os
from os.path import dirname, abspath

othello_dir = os.path.join(dirname(dirname(abspath(__file__))),
                           "othello")
sys.path.insert(0, othello_dir)
from game import State

lib = cdll.LoadLibrary("./players/cAI/cAI.so")

state_8 = c_int * 8
state_8_8 = state_8 * 8


class cAI(Player):

    def move(self, board):
        c_board = state_8_8(*[state_8(*row) for row in board])
        max_time = c_double(self.max_time - 1)

        move_i = lib.findMove(c_board, self.color, max_time)
        return (move_i & 63, (move_i & (63 << 6)) >> 6)

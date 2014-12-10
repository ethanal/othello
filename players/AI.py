from . import Player
from time import sleep


class AI(Player):
    def move(self, board):
        sleep(4)
        return board.legal_moves(self.color)[0]

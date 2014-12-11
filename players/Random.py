from . import Player
from random import choice


class Random(Player):

    def move(self, board):
        moves = board.legal_moves(self.color)
        if len(moves) > 0:
            return choice(moves)
        return None

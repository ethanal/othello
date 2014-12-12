from random import choice
from time import sleep
from . import Player


class ExampleAI(Player):

    def move(self, board):
        sleep(5)
        moves = board.legal_moves(self.color)
        if len(moves) != 0:
            return choice(moves)
        return None

from . import Player


class Human(Player):

    def move(self, board):
        return self.get_user_move()

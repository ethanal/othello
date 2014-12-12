class Player(object):

    def __init__(self, color, get_user_move):
        self.color = color
        self.get_user_move = get_user_move

    def move(self, board):
        raise Exception("Method 'move' not implemented")

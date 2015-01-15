class Player(object):

    def __init__(self, color, get_user_move, max_time):
        self.color = color
        self.get_user_move = get_user_move
        self.max_time = max_time

    def move(self, board):
        raise Exception("Method 'move' not implemented")

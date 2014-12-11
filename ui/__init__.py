class UI:

    def __init__(self, game):
        self.game = game

    def get_move(self):
        raise Exception("Method 'get_move' not implemented.")

    def update(self):
        raise Exception("Method 'update' not implemented.")

    def run(self, mainloop):
        return mainloop()

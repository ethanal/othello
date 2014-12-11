import multiprocessing as mp


class UI:

    def __init__(self, game):
        parent_conn, child_conn = mp.Pipe(duplex=False)
        self.ui_event_pipe = parent_conn
        self.game = game

    def get_move(self):
        raise Exception("Method 'get_move' not implemented.")

    def update(self):
        raise Exception("Method 'update' not implemented.")

    def run(self, mainloop):
        return mainloop()

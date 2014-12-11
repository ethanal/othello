import tkinter
import multiprocessing as mp
import threading
import os

from . import UI

import sys
sys.path.insert(0, "..")
from game import State


class GraphicalUI(UI):
    GREEN = "#207910"
    WHITE = "#ffffff"
    BLACK = "#000000"

    def __init__(self, game):
        super(GraphicalUI, self).__init__(game)

        disk_padding = 7

        self.root = tkinter.Tk()
        self.root.title("Othello")
        self.root.geometry("460x500")
        self.root.resizable(width=False, height=False)
        self.canvas = tkinter.Canvas(self.root,
                                     width=460,
                                     height=500,
                                     highlightthickness=0)

        self.canvas.create_rectangle(30, 70,
                                     430, 470,
                                     fill=GraphicalUI.GREEN,
                                     width=2)
        for i in range(1, 8):
            self.canvas.create_line(30 + i * 50, 70,
                                    30 + i * 50, 470,
                                    width=2)
            self.canvas.create_line(30, 70 + i * 50,
                                    430, 70 + i * 50,
                                    width=2)

        self.player_1_title = tkinter.StringVar()
        self.player_1_title.set("Black")
        self.player_1_label = tkinter.Label(
            self.root,
            textvariable=self.player_1_title,
            fg=GraphicalUI.GREEN,
            padx=20,
            pady=10
        )
        self.player_1_label.place(relx=0, anchor=tkinter.NW)

        self.player_2_title = tkinter.StringVar()
        self.player_2_title.set("White")
        self.player_2_label = tkinter.Label(
            self.root,
            textvariable=self.player_2_title,
            padx=20,
            pady=10
        )
        self.player_2_label.place(relx=1, anchor=tkinter.NE)

        self.disks = []
        for row in range(8):
            dy = row * 50
            self.disks.append([])
            for col in range(8):
                dx = col * 50

                disk = self.canvas.create_oval(30 + disk_padding + dx,
                                               70 + disk_padding + dy,
                                               30 + 50 - disk_padding + dx,
                                               70 + 50 - disk_padding + dy,
                                               fill=GraphicalUI.GREEN,
                                               width=0)
                self.disks[row].append(disk)

        self.canvas.pack()

        self.accepting_moves = False
        self.parent_click_pipe, self.child_click_pipe = mp.Pipe(duplex=False)

        def click(event):
            if self.accepting_moves:
                if (30 <= event.x <= 430) and (70 <= event.y <= 470):
                    row = (event.y - 70) // 50
                    col = (event.x - 30) // 50
                    self.child_click_pipe.send((row, col))
                    self.accepting_moves = False

        self.root.bind("<Button-1>", click)

    def run(self, mainloop):
        t = threading.Thread(target=mainloop)
        self.root.after(0, t.start)

        def abort():
            os._exit(0)

        self.root.bind("<q>", lambda e: abort())
        self.root.protocol("WM_DELETE_WINDOW", abort)

        self.root.mainloop()

    def get_move(self):
        self.accepting_moves = True
        return self.parent_click_pipe.recv()

    def update(self):
        p1_name = self.game.players[0].__class__.__name__
        p2_name = self.game.players[1].__class__.__name__
        p1_count = self.game.board.count(State.black)
        p2_count = self.game.board.count(State.white)
        self.player_1_title.set("Black ({})\n"
                                "{} disks".format(p1_name, p1_count))
        self.player_2_title.set("White ({})\n"
                                "{} disks".format(p2_name, p2_count))

        self.player_1_label.configure(
            fg=(GraphicalUI.GREEN if self.game.player is State.black else
                GraphicalUI.BLACK)
        )

        self.player_2_label.configure(
            fg=(GraphicalUI.GREEN if self.game.player is State.white else
                GraphicalUI.BLACK)
        )

        for row in range(8):
            for col in range(8):
                colors = {
                    State.white: GraphicalUI.WHITE,
                    State.black: GraphicalUI.BLACK,
                    State.empty: GraphicalUI.GREEN
                }
                color = colors[self.game.board.board[row][col]]
                self.canvas.itemconfig(self.disks[row][col], fill=color)

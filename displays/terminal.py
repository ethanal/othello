import os
import platform
from . import Display


class TerminalDisplay(Display):
    def update(self, game):
        print("".join("".join(str(j) for j in i) + "\n" for i in game.board.board)[:-1].replace("0", "."))

    def _clear(self):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

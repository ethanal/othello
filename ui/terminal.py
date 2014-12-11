from . import UI

import sys
sys.path.insert(0, "..")
from game import State


class TerminalUI(UI):

    def __init__(self, game):
        super(TerminalUI, self).__init__(game)
        print(" Black      White\n"
              "  ###        ... \n"
              " #####      .....\n"
              "  ###        ... \n")

    def get_move(self):
        spot = ""
        while not (len(spot) == 2 and
                   ord("a") <= ord(spot[0].lower()) <= ord("h") and
                   ord("1") <= ord(spot[1]) <= ord("8")):
            spot = input("Your move: ")
            if spot.lower() == "pass":
                return None

        return (int(spot[1]) - 1, ord(spot[0].lower()) - ord("a"))

    def update(self):
        def char_for_state(s):
            return ("#" if s is State.black else
                    "." if s is State.white else " ")

        letters = "  " + " ".join("   " + c + "   " for c in "abcdefgh") + "  "
        row_divider = " " + "+-------" * 8 + "+ "

        print(letters)
        print(row_divider)

        for row in range(8):
            print(" |", end="")
            for col in range(8):
                c = char_for_state(self.game.board.board[row][col])
                print("  {}  |".format(c*3), end="")
            print(" ")

            print(str(row + 1) + "|", end="")
            for col in range(8):
                c = char_for_state(self.game.board.board[row][col])
                print(" {} |".format(c*5), end="")
            print(str(row + 1))

            print(" |", end="")
            for col in range(8):
                c = char_for_state(self.game.board.board[row][col])
                print("  {}  |".format(c*3), end="")
            print(" ")

            print(row_divider)

        print(letters)

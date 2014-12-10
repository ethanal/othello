from . import Player


class Human(Player):
    def move(self, board):
        return board.legal_moves(self.color)[0]


    # def __getitem__(self, index):
    #     """Use subscript notation (like array[2]) on an OthelloBoard
    #     object to access the internal matrix representation directly.
    #     The index can be in one of two forms:

    #     - an integer, which will fetch the appropriate row of the board
    #     - a 2-character string in the form [a-f][1-8] (e.g. d3 or a4)

    #     The integer form is row-column and string form is column-row.
    #     Therefore, my_board[3][4] is equivalent to my_board["e4"]

    #     """

    #     if isinstance(index, int):
    #         return self.board[index]
    #     elif (isinstance(index, str) and
    #           len(index) == 2 and
    #           ord("a") <= ord(index[0].lower()) <= ord("h") and
    #           index[1] in range(1, 9)):
    #         return self.board[ord(index[0].lower()) - ord("a")][index[1]]
    #     else:
    #         raise IndexError()

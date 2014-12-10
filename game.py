from copy import deepcopy
import multiprocessing as mp
import queue
from players.Human import Human

try:
    from displays.gui import GraphicalDisplay
    _default_display = GraphicalDisplay
except:
    from displays.terminal import TerminalDisplay
    _default_display = TerminalDisplay


class State:
    empty = 0
    black = 1
    white = 2

    @staticmethod
    def opponent(state):
        if state is State.empty:
            raise Exception("Can not find opponent of empty state")
        elif state is State.white:
            return State.black
        elif state is State.black:
            return State.white
        else:
            raise Exception("Invalid state")

    @staticmethod
    def player_name(state):
        return "black" if state is State.black else "white"


class InvalidMoveException(Exception):
    pass


class OthelloBoard:
    directions = ((-1, 0),   # N
                  (-1, 1),   # NE
                  (0, 1),    # E
                  (1, 1),    # SE
                  (1, 0),    # S
                  (1, -1),   # SW
                  (0, -1),   # W
                  (-1, -1))  # NW

    def __init__(self):
        # self.board uses the form self.board[row][column]
        self.board = [[State.empty for i in range(8)] for j in range(8)]
        self.board[3][3] = State.white
        self.board[3][4] = State.black
        self.board[4][3] = State.black
        self.board[4][4] = State.white

    def move_would_capture(self, row, col, player):
        opponent = State.opponent(player)

        for drow, dcol in OthelloBoard.directions:
            rowp = row + drow
            colp = col + dcol

            if not (0 <= rowp <= 7 and
                    0 <= colp <= 7 and
                    self.board[rowp][colp] is opponent):
                continue

            while (0 <= rowp <= 7 and
                   0 <= colp <= 7 and
                   self.board[rowp][colp] is opponent):
                rowp += drow
                colp += dcol
            if 0 <= rowp <= 7 and 0 <= colp <= 7 and \
               self.board[rowp][colp] is player:
                return True

        return False

    def legal_moves(self, player):
        if player is not State.white and player is not State.black:
            raise Exception("Invalid player")

        possible = []
        for row in range(8):
            for col in range(8):
                if self.board[row][col] is State.empty:
                    if self.move_would_capture(row, col, player):
                        possible.append((row, col))
        return possible

    def make_move(self, row, col, player):
        if not self.move_would_capture(row, col, player):
            raise InvalidMoveException()

        self.board[row][col] = player

        opponent = State.opponent(player)
        for drow, dcol in OthelloBoard.directions:
            rowp = row + drow
            colp = col + dcol

            if not (0 <= rowp <= 7 and
                    0 <= colp <= 7 and
                    self.board[rowp][colp] is opponent):
                continue

            while (0 <= rowp <= 7 and 0 <= colp <= 7 and
                   self.board[rowp][colp] is opponent):
                rowp += drow
                colp += dcol

            if (0 <= rowp <= 7 and 0 <= colp <= 7 and self.board[rowp][colp] is player):
                rowp -= drow
                colp -= dcol

                while not (rowp == row and colp == col):
                    self.board[rowp][colp] = player

                    rowp -= drow
                    colp -= dcol

    def count(self, player):
        total = 0
        for row in range(8):
            for col in range(8):
                if self.board[row][col] is player:
                    total += 1
        return total


class OthelloGame:
    def __init__(self, player_1, player_2, display=_default_display):
        self.players = (player_1(State.black), player_2(State.white))
        self.display = display()
        self.board = OthelloBoard()
        self.player = State.black
        self.moves = []

    def next_player(self):
        opp = State.opponent(self.player)
        opp_index = (State.black, State.white).index(opp)
        if (len(self.moves) % 2) != opp_index:
            raise Exception("Can not advance to next player before current "
                            "player makes a move")
        self.player = opp
        return self.players[opp_index]

    @staticmethod
    def _make_move_with_timeout(q, player, board):
        q.put(player.move(board))

    def start(self):
        player = self.players[0]
        squares = 0
        stuck = 0
        timeout = 10

        while squares < 64 and stuck < 2:
            print(State.player_name(self.player).capitalize() + "'s turn")
            self.display.update(self)
            if isinstance(player, Human):
                move = player.move(deepcopy(self.board))
            else:
                q = mp.Queue()
                p = mp.Process(target=OthelloGame._make_move_with_timeout,
                               args=(q, player, deepcopy(self.board)))
                p.start()
                try:
                    move = q.get(timeout=timeout)
                except queue.Empty:
                    if p.is_alive():
                        p.terminate()

                    if self.player is State.black:
                        print("Black is disqualified for taking too much time.")
                        return State.white
                    else:
                        print("White is disqualified for taking too much time.")
                        return State.black

            print(State.player_name(self.player).capitalize(), "moves", move)
            self.moves.append(move)
            self.board.make_move(move[0], move[1], self.player)
            player = self.next_player()
            print()

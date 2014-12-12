from copy import deepcopy
import multiprocessing as mp
import queue
from players.Human import Human


class State(object):
    empty = 0
    black = 1
    white = 2
    draw = 3

    @staticmethod
    def opponent(state):
        if state is State.white:
            return State.black
        elif state is State.black:
            return State.white
        else:
            raise Exception("Can not find opponent of this state")

    @staticmethod
    def player_name(state):
        return "black" if state is State.black else "white"


class InvalidMoveException(Exception):
    pass


class OthelloBoard(object):
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

            if 0 <= rowp <= 7 and \
               0 <= colp <= 7 and \
               self.board[rowp][colp] is player:
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


class OthelloGame(object):
    TIMEOUT = 10

    def __init__(self, player_1, player_2, ui=None):
        if ui is None:
            try:
                from ui.gui import GraphicalUI
                ui = GraphicalUI
            except:
                from ui.terminal import TerminalUI
                ui = TerminalUI
        ui = ui(self)
        self.ui = ui

        def raise_exception():
            raise Exception("Only Human players can get moves from the user.")

        get_move_1 = ui.get_move if player_1 is Human else raise_exception
        get_move_2 = ui.get_move if player_2 is Human else raise_exception

        self.players = (player_1(State.black, get_move_1),
                        player_2(State.white, get_move_2))
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

    def play(self):
        parent_return_pipe, child_return_pipe = mp.Pipe(duplex=False)

        def mainloop():
            player = self.players[0]
            squares = 4
            stuck = 0
            turn = 1

            while squares < 64 and stuck < 2:
                move_title = ("#" + str(turn) + ": " +
                              State.player_name(self.player).capitalize() +
                              "'s turn")
                print(move_title)
                print("-" * len(move_title))
                self.ui.update()

                if isinstance(player, Human):
                    move = player.move(deepcopy(self.board))
                else:
                    q = mp.Queue()
                    p = mp.Process(target=OthelloGame._make_move_with_timeout,
                                   args=(q, player, deepcopy(self.board)))
                    p.start()
                    try:
                        move = q.get(timeout=OthelloGame.TIMEOUT)
                    except queue.Empty:
                        if p.is_alive():
                            p.terminate()

                        if self.player is State.black:
                            print("Black is disqualified for "
                                  "taking too much time.")
                            child_return_pipe.send(State.white)
                        else:
                            print("White is disqualified for "
                                  "taking too much time.")
                            child_return_pipe.send(State.black)
                        return

                possible = self.board.legal_moves(self.player)

                if move is not None:
                    if move not in possible:
                        if self.player is State.black:
                            print("Black is disqualified for "
                                  "making an illegal move.")
                            child_return_pipe.send(State.white)
                        else:
                            print("White is disqualified for "
                                  "making an illegal move.")
                            child_return_pipe.send(State.black)
                        return

                    self.board.make_move(move[0], move[1], self.player)

                    move_code = "abcdefgh"[move[1]] + str(move[0] + 1)
                    print(State.player_name(self.player).capitalize(), "moves",
                          move_code)
                    print("Black: ", self.board.count(State.black), "disks")
                    print("White: ", self.board.count(State.white), "disks")
                    stuck = 0
                elif len(possible) == 0:
                    stuck += 1
                    print(State.player_name(self.player).capitalize(), "passes")
                else:
                    if self.player is State.black:
                        print("Black is disqualified for passing illegally.")
                        child_return_pipe.send(State.white)
                    else:
                        print("White is disqualified for passing illegally.")
                        child_return_pipe.send(State.black)
                    return

                self.moves.append(move)
                squares += 1
                turn += 1
                player = self.next_player()
                print()

            print("Results\n-----------")
            self.ui.update()

            white = self.board.count(State.white)
            black = self.board.count(State.black)

            if white == black:
                print("Draw")
                child_return_pipe.send(State.draw)
            elif white > black:
                print("White wins")
                child_return_pipe.send(State.white)
            else:
                print("Black wins")
                child_return_pipe.send(State.black)

        self.ui.run(mainloop)
        return parent_return_pipe.recv()

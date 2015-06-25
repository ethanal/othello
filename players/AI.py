from . import Player
from copy import deepcopy
import sys
from time import time

sys.path.insert(0, "..")
from game import OthelloBoard, State


# http://mkorman.org/othello.pdf


class GameState(object):

    def __init__(self, board, parent=None, depth=None, player=None, move=None):
        self.board = board
        self.children = {}
        self.depth = depth
        self.parent = parent
        self.player = player
        self.move = move
        self.hash = None
        self.score = 0

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        if self.hash is not None:
            return self.hash
        s = "".join("".join(map(str, row)) for row in self.board.board)
        self.hash = hash(s)
        return self.hash

    def __repr__(self):
        return "<GameState: {} {}>".format(State.player_name(self.player),
                                           self.score)


class AI(Player):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_time -= 1

    def evaluate(self, state):
        # state.score = state.board.count(State.black) - state.board.count(State.white)
        # return state.score
        def p():
            # Piece difference
            B = state.board.count(State.black)
            W = state.board.count(State.white)

            if B > W:
                return 100 * B / (B + W)
            elif B < W:
                return -100 * W / (B + W)
            else:
                return 0

        def c():
            # Corner occupancy
            B = W = 0
            for row, col in [(0, 0), (0, 7), (7, 0), (7, 7)]:
                if state.board[row][col] is State.black:
                    B += 1
                elif state.board[row][col] is State.white:
                    W += 1
            return 25 * B - 25 * W

        def l():
            # Corner closeness
            B = W = 0
            for corner, adj in {(0, 0): ((0, 1), (1, 1), (1, 0)),
                                (0, 7): ((0, 6), (1, 6), (1, 7)),
                                (7, 0): ((6, 0), (6, 1), (7, 1)),
                                (7, 7): ((7, 6), (6, 6), (6, 7))}.items():
                if state.board[corner[0]][corner[1]] is State.empty:
                    for row, col in adj:
                        if state.board[row][col] is State.black:
                            B += 1
                        elif state.board[row][col] is State.white:
                            W += 1
            return -12.5 * B + 12.5 * W

        def m():
            # Mobility
            B = len(state.board.legal_moves(State.black))
            W = len(state.board.legal_moves(State.white))

            if B > W:
                return 100 * B / (B + W)
            elif B < W:
                return -100 * W / (B + W)
            return 0

        def f():
            # Frontier disks
            B = W = 0
            for row in range(8):
                for col in range(8):
                    if state.board[row][col] is State.empty:
                        continue

                    for drow, dcol in OthelloBoard.directions:
                        rowp = row + drow
                        colp = col + dcol

                        if 0 <= rowp <= 7 and 0 <= colp <= 7:
                            if state.board[rowp][colp] is State.empty:
                                if state.board[row][col] is State.black:
                                    B += 1
                                if state.board[row][col] is State.white:
                                    W += 1
            if B > W:
                return -100 * B / (B + W)
            elif B < W:
                return 100 * W / (B + W)
            return 0

        def d():
            # Disk squares
            V = [[20, -3, 11, 8, 8, 11, -3, 20],
                 [-3, -7, -4, 1, 1, -4, -7, -3],
                 [11, -4, 2, 2, 2, 2, -4, 11],
                 [8, 1, 2, -3, -3, 2, 1, 8],
                 [8, 1, 2, -3, -3, 2, 1, 8],
                 [11, -4, 2, 2, 2, 2, -4, 11],
                 [-3, -7, -4, 1, 1, -4, -7, -3],
                 [20, -3, 11, 8, 8, 11, -3, 20]]

            total = 0
            for row in range(8):
                for col in range(8):
                    sigma = {
                        State.black: 1,
                        State.empty: 0,
                        State.white: -1
                    }[state.board[row][col]]
                    total += V[row][col] * sigma
            return total

        weights = (10, 801.724, 382.026, 78.922, 74.396, 10)
        heuristics = (p(), c(), l(), m(), f(), d())
        score = sum(weights[i] * heuristics[i] for i in range(len(heuristics)))
        state.score = score
        return score

    def move(self, board):
        start_time = time()
        best_move = None

        plies = 0
        max_plies = 64 - board.total_count()

        while True:
            plies += 1

            if plies > max_plies or (time() - start_time) >= self.max_time:
                return best_move

            def search(state, alpha, beta):
                if (time() - start_time) >= self.max_time:
                    return -1

                player = State.opponent(state.player)
                moves = state.board.legal_moves(player)

                if state.depth == plies or len(moves) == 0:
                    self.evaluate(state)
                else:
                    for move in moves:
                        next_board = deepcopy(state.board)
                        next_board.make_move(move[0], move[1], player)
                        next_state = GameState(next_board,
                                               parent=state,
                                               player=player,
                                               depth=state.depth+1,
                                               move=move)
                        ret = search(next_state, alpha, beta)
                        if ret == -1:
                            return ret

                        if state.player is State.black:
                            alpha = max(alpha, next_state.score)
                            state.score = alpha
                        else:
                            beta = min(beta, next_state.score)
                            state.score = beta

                        if alpha >= beta:
                            break

                        state.children[move] = next_state

            initial_player = State.opponent(self.color)
            current_state = GameState(board, depth=0, player=initial_player)
            ret = search(current_state, float("-inf"), float("inf"))

            if ret == -1:
                return best_move

            scores = [(s.score, m) for m, s in current_state.children.items()]

            if len(scores) == 0:
                # pass
                return None

            if self.color is State.black:
                best_score, best_move = max(scores)
            else:
                best_score, best_move = min(scores)

            s = "abcdefgh"[best_move[1]] + str(best_move[0] + 1)
            print("Searched {} plies and got {} ({})".format(plies,
                                                             s,
                                                             best_score))

        return best_move

#include <stdio.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>


typedef int Board[8][8];

static double INF = 99999999999999;
static bool ANSI_COLORS = false;

typedef struct Coord {
    int r;
    int c;
} Coord;

typedef enum {
    EMPTY = 0,
    BLACK = 1,
    WHITE = 2,
    DRAW = 3
} State;


struct GameState {
    Board board;
    struct GameState *children[64];
    int numChildren;
    int depth;
    State player;
    Coord move;
    double score;
    int numWhite;
    int numBlack;
    int numEmpty;
};
typedef struct GameState GameState;

Coord DIRECTIONS[8] = {
    {-1,  0}, // N
    {-1,  1}, // NE
    { 0,  1}, // E
    { 1,  1}, // SE
    { 1,  0}, // S
    { 1, -1}, // SW
    { 0, -1}, // W
    {-1, -1}  // NW
};

int coordToInt(Coord c) {
    return c.r + (c.c << 6);
}

Coord intToCoord(int i) {
    Coord c = {i & 63, (i & (63 << 6)) >> 6};
    return c;
}

double getWallTime(){
    struct timeval time;
    if (gettimeofday(&time, NULL)){
        return 0;
    }
    return (double)time.tv_sec + (double)time.tv_usec * 0.000001;
}

void copyBoard(Board dest, Board src) {
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) {
            dest[i][j] = src[i][j];
        }
    }
}

void printBoard(Board board) {
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) {
            if (board[i][j] == BLACK) {
                if (ANSI_COLORS)
                    printf("\033[30m\033[42m * \033[00m");
                else
                    printf(" B ");
            } else if (board[i][j] == WHITE) {
                if (ANSI_COLORS)
                    printf("\033[37m\033[42m * \033[00m");
                else
                    printf(" W ");
            } else {
                if (ANSI_COLORS)
                    printf("\033[42m . \033[00m");
                else
                    printf(" . ");
            }
        }
        printf("\n");
    }
}

void updateStateCounts(GameState *state) {
    state->numBlack = 0;
    state->numWhite = 0;
    state->numEmpty = 0;

    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) {
            switch (state->board[i][j]) {
                case BLACK:
                    state->numBlack++;
                    break;
                case WHITE:
                    state->numWhite++;
                    break;
                case EMPTY:
                    state->numEmpty++;
                    break;
            }
        }
    }
}

State getOpponent(State s) {
    if (s == BLACK)
        return WHITE;
    return BLACK;
}

bool moveWouldCapture(Board board, int row, int col, State player) {
    State opponent = getOpponent(player);

    for (int i = 0; i < 8; ++i) {
        int drow = DIRECTIONS[i].r;
        int dcol = DIRECTIONS[i].c;

        int rowp = row + drow;
        int colp = col + dcol;

        if (!(0 <= rowp && rowp <= 7 &&
              0 <= colp && colp <= 7 &&
              board[rowp][colp] == opponent))
            continue;

        while (0 <= rowp && rowp <= 7 &&
               0 <= colp && colp <= 7 &&
               board[rowp][colp] == opponent) {
            rowp += drow;
            colp += dcol;
        }

        if (0 <= rowp && rowp <= 7 &&
            0 <= colp && colp <= 7 &&
            board[rowp][colp] == player)
            return true;
    }

    return false;
}

void legalMoves(Board board, State player, Coord moves[64], int *numMoves) {
    *numMoves = 0;
    for (int row = 0; row < 8; ++row) {
        for (int col = 0; col < 8; ++col) {
            if (board[row][col] == EMPTY) {
                if (moveWouldCapture(board, row, col, player)) {
                    moves[(*numMoves)++] = (Coord){row, col};
                }
            }
        }
    }

}

void makeMove(Board board, Coord pos, State player) {
    int row = pos.r;
    int col = pos.c;

    board[row][col] = player;

    State opponent = getOpponent(player);
    for (int i = 0; i < 8; ++i) {
        int drow = DIRECTIONS[i].r;
        int dcol = DIRECTIONS[i].c;
        int rowp = row + drow;
        int colp = col + dcol;

        if (!(0 <= rowp && rowp <= 7 &&
              0 <= colp && colp <= 7 &&
              board[rowp][colp] == opponent))
            continue;

        while (0 <= rowp && rowp <= 7 &&
               0 <= colp && colp <= 7 &&
               board[rowp][colp] == opponent) {
            rowp += drow;
            colp += dcol;
        }

        if (0 <= rowp && rowp <= 7 &&
            0 <= colp && colp <= 7 &&
            board[rowp][colp] == player) {
            rowp -= drow;
            colp -= dcol;

            while (!(rowp == row && colp == col)) {
                board[rowp][colp] = player;

                rowp -= drow;
                colp -= dcol;
            }
        }
    }
}

void evaluate(GameState *state) {
    updateStateCounts(state);

    int B;
    int W;

    // Piece difference
    double P;
    B = state->numBlack;
    W = state->numWhite;
    if (B > W) {
        P = 100.0 * B / (B + W);
    } else if (B < W) {
        P = 100.0 * W / (B + W);
    } else {
        P = 0.0;
    }

    // Corner occupancy
    double C;
    B = 0;
    W = 0;
    int corners[4][2] = {{0, 0}, {0, 7}, {7, 0}, {7, 7}};
    for (int i = 0; i < 4; ++i) {
        if (state->board[corners[i][0]][corners[i][1]] == BLACK)
            B++;
        else if (state->board[corners[i][0]][corners[i][1]] == WHITE)
            W++;
    }
    C = 25.0 * B - 25.0 * W;


    // Corner closeness
    double L;
    B = 0;
    W = 0;
    int cornerAdj[4][3][2] = {{{0, 1}, {1, 1}, {1, 0}},
                              {{0, 6}, {1, 6}, {1, 7}},
                              {{6, 0}, {6, 1}, {7, 1}},
                              {{7, 6}, {6, 6}, {6, 7}}};
    for (int i = 0; i < 4; ++i) {
        if (state->board[corners[i][0]][corners[i][1]] == EMPTY) {
            for (int j = 0; j < 3; ++j) {
                int row = cornerAdj[i][j][0];
                int col = cornerAdj[i][j][1];
                if (state->board[row][col] == BLACK) {
                    B++;
                } else if (state->board[row][col] == WHITE) {
                    W++;
                }
            }
        }
    }
    L = -12.5 * B + 12.5 * W;


    // Mobility
    double M;
    B = 0;
    W = 0;
    for (int i = 0; i < 8; ++i) {
        for (int j = 0; j < 8; ++j) {
            if (state->board[i][j] == EMPTY) {
                if (moveWouldCapture(state->board, i, j, BLACK)) {
                    B++;
                }
                if (moveWouldCapture(state->board, i, j, WHITE)) {
                    W++;
                }
            }
        }
    }
    if (B > W)
        M = 100.0 * B / (B + W);
    else if (B < W)
        M = -100.0 * W / (B + W);
    else
        M = 0.0;


    // Frontier disks
    double F;
    B = 0;
    W = 0;
    for (int row = 0; row < 8; ++row) {
        for (int col = 0; col < 8; ++col) {
            if (state->board[row][col] == EMPTY)
                continue;

            for (int di = 0; di < 8; ++di) {
                int rowp = row + DIRECTIONS[di].r;
                int colp = col + DIRECTIONS[di].c;

                if ((0 <= rowp <= 7) && (0 <= colp <= 7)) {
                    if (state->board[rowp][colp] == EMPTY) {
                        if (state->board[row][col] == BLACK)
                            B++;
                        else if (state->board[row][col] == WHITE)
                            W++;
                    }
                }
            }
        }
    }
    if (B > W)
        F = -100.0 * B / (B + W);
    else if (B < W)
        F = 100.0 * W / (B + W);
    else
        F = 0.0;

    // Disk squares
    double D = 0.0;
    int V[8][8] = {{20, -3, 11,  8,  8, 11, -3, 20},
                   {-3, -7, -4,  1,  1, -4, -7, -3},
                   {11, -4,  2,  2,  2,  2, -4, 11},
                   { 8,  1,  2, -3, -3,  2,  1,  8},
                   { 8,  1,  2, -3, -3,  2,  1,  8},
                   {11, -4,  2,  2,  2,  2, -4, 11},
                   {-3, -7, -4,  1,  1, -4, -7, -3},
                   {20, -3, 11,  8,  8, 11, -3, 20}};
    for (int row = 0; row < 8; ++row) {
        for (int col = 0; col < 8; ++col) {
            if (state->board[row][col] == BLACK)
                D += V[row][col] * 1.0;
            else if (state->board[row][col] == WHITE)
                D += V[row][col] * -1.0;
        }
    }

    double weights[6] = {10.0, 801.724, 382.026, 78.922, 74.396, 10.0};
    double heuristics[6] = {P, C, L, M, F, D};
    double score = 0.0;
    for (int i = 0; i < 6; ++i)
        score += weights[i] * heuristics[i];
    state->score = score;
}


bool search(GameState *state,
            double alpha,
            double beta,
            double startTime,
            double maxTime,
            int plies) {
    if ((getWallTime() - startTime) >= maxTime)
        return false;

    State player = getOpponent(state->player);
    Coord moves[64];
    int numMoves;
    legalMoves(state->board, player, moves, &numMoves);

    if ((state->depth == plies) || (numMoves == 0)) {
        evaluate(state);
    } else {
        for (int i = 0; i < numMoves; ++i) {
            Coord move = moves[i];
            GameState *nextState = malloc(sizeof(GameState));
            copyBoard(nextState->board, state->board);
            makeMove(nextState->board, move, player);
            nextState->player = player;
            nextState->depth = state->depth + 1;
            nextState->numChildren = 0;
            nextState->move = move;


            bool success = search(nextState, alpha, beta, startTime, maxTime, plies);

            if (!success) {
                free(nextState);
                return false;
            }

            if (state->player == BLACK) {
                alpha = (alpha > nextState->score ? alpha : nextState->score); // max
                state->score = alpha;
            } else {
                beta = (beta < nextState->score ? beta : nextState->score); // min
                state->score = beta;
            }

            if (alpha >= beta) {
                free(nextState);
                break;
            }

            if (state->depth == 0) {
                state->children[(state->numChildren)++] = nextState;
            } else {
                free(nextState);
            }
        }
    }

    return true;
}


int findMove(Board board, State color, double maxTime) {
    double startTime = getWallTime();
    Coord bestMove;
    int plies = 0;

    GameState state;
    copyBoard(state.board, board);
    state.depth = 0;
    state.player = getOpponent(color);

    while (true) {
        plies++;

        state.numChildren = 0;

        updateStateCounts(&state);
        int maxPlies = 64 - (state.numBlack + state.numWhite);

        if (plies > maxPlies || (getWallTime() - startTime) >= maxTime)
            return coordToInt(bestMove);

        bool success = search(&state, -INF, INF, startTime, maxTime, plies);

        if (!success)
            return coordToInt(bestMove);

        if (state.numChildren == 0)
            return -1;

        double bestScore = state.children[0]->score;
        bestMove = state.children[0]->move;
        free(state.children[0]);
        for (int i = 1; i < state.numChildren; ++i) {
            bool newBest;
            if (color == BLACK) {
                newBest = state.children[i]->score >= bestScore;
            } else {
                newBest = state.children[i]->score <= bestScore;
            }

            if (newBest) {
                bestScore = state.children[i]->score;
                bestMove = state.children[i]->move;
            }
            free(state.children[i]);
        }

        printf("Searched %d plies and got %d, %d (%f)\n", plies, bestMove.r, bestMove.c, bestScore);
    }


    return coordToInt(bestMove);
}

int main() {
    Board board = {{0, 0, 0, 0, 0, 0, 0, 0},
                   {0, 0, 0, 0, 0, 0, 0, 0},
                   {0, 0, 0, 0, 0, 0, 0, 0},
                   {0, 0, 0, 2, 1, 0, 0, 0},
                   {0, 0, 0, 1, 2, 0, 0, 0},
                   {0, 0, 0, 0, 0, 0, 0, 0},
                   {0, 0, 0, 0, 0, 0, 0, 0},
                   {0, 0, 0, 0, 0, 0, 0, 0}};
    int m = findMove(board, BLACK, 5.0);
    Coord c = intToCoord(m);
    printBoard(board);
    printf("\n");
    makeMove(board, c, BLACK);
    printBoard(board);
    printf("Move: %d, %d\n", c.r, c.c);
}

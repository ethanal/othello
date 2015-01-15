#!/usr/bin/env python3
# Ethan Lowman, 2014

import argparse
import sys
from game import OthelloGame, State


def has_tkinter():
    try:
        import tkinter
    except ImportError:
        return False
    else:
        return True


def main(argv):
    parser = argparse.ArgumentParser(description="Othello Moderator")
    ui_group = parser.add_mutually_exclusive_group(required=False)

    ui_group.add_argument(
        "-g",
        "--graphical",
        action="store_true",
        help="Use a graphical UI"
    )
    ui_group.add_argument(
        "-t",
        "--terminal",
        action="store_true",
        help="Use a text-based UI"
    )

    parser.add_argument(
        "-n",
        "--repeated-trials",
        type=int,
        help="The number of repeated trials to run for a round "
             "robin tournament."
    )

    parser.add_argument(
        "-T",
        "--timeout",
        type=int,
        help="The maximum amount of time (seconds) to allow AIs for each move."
    )

    parser.add_argument("players", nargs="*")

    args = parser.parse_args(argv)

    if not args.graphical and not args.terminal:
        args.graphical = True

    if has_tkinter() and args.graphical:
        from ui.gui import GraphicalUI
        ui = GraphicalUI
    else:
        from ui.terminal import TerminalUI
        ui = TerminalUI

    players = args.players
    if len(players) == 0:
        print("Running tournament...")

    elif len(players) == 2:
        try:
            module_1 = __import__("players." + players[0],
                                  fromlist=[players[0]])
            player_1 = getattr(module_1, players[0])
        except (ImportError, AttributeError) as e:
            if "No module named 'players" in str(e):
                print("Player '{}' does not exist".format(players[0]))
                exit(1)
            else:
                raise e

        try:
            module_2 = __import__("players." + players[1],
                                  fromlist=[players[1]])
            player_2 = getattr(module_2, players[1])
        except (ImportError, AttributeError) as e:
            if "No module named 'players" in str(e):
                print("Player '{}' does not exist".format(players[1]))
                exit(1)
            else:
                raise e

        game = OthelloGame(player_1, player_2, ui=ui, timeout=args.timeout)
        game.play()
    else:
        print("Provide the names of two players as arguments or provide "
              "no names to run a tournament.")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        exit(1)

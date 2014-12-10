#!/usr/bin/env python3
# Ethan Lowman, 2014

import argparse
import sys
from game import OthelloGame


def has_tkinter():
    try:
        import tkinter
    except ImportError:
        return False
    else:
        return True


def main(argv):
    parser = argparse.ArgumentParser(description="Othello Moderator")
    display_group = parser.add_mutually_exclusive_group(required=False)

    display_group.add_argument(
        "-g",
        "--graphical",
        action="store_true",
        help="Use a graphical display"
    )
    display_group.add_argument(
        "-t",
        "--terminal",
        action="store_true",
        help="Use a text-based display"
    )

    parser.add_argument("players", nargs="*")

    args = parser.parse_args(argv)

    if not args.graphical and not args.terminal:
        args.graphical = True

    if has_tkinter() and args.graphical:
        from displays.gui import GraphicalDisplay
        display = GraphicalDisplay
    else:
        from displays.terminal import TerminalDisplay
        display = TerminalDisplay

    players = args.players
    if len(players) == 0:
        print("Running tournament...")
    elif len(players) == 2:
        try:
            module_1 = __import__("players." + players[0], fromlist=[players[0]])
            player_1 = getattr(module_1, players[0])
        except (ImportError, AttributeError):
            print("Player '{}' does not exist".format(players[0]))
            exit(1)

        try:
            module_2 = __import__("players." + players[1], fromlist=[players[1]])
            player_2 = getattr(module_2, players[1])
        except (ImportError, AttributeError):
            print("Player '{}' does not exist".format(players[1]))
            exit(1)

        game = OthelloGame(player_1, player_2, display=display)
        game.start()
    else:
        print("Provide the names of two players as arguments or provide "
              "no names to run a tournament.")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        exit(1)

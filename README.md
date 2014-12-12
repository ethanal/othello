# Othello Moderator

A Python 3 Othello moderator. To add an AI, write a submodule of the `players` module that contains a subclass of `players.Player`. For the AI to be detected, the class name must be the same as the module name (the filename without the .py extension).

To run the moderator, run `./moderator.py Human AI` where the two arguments are the first and second player types respectively. Optionally, include a `-t` or `-g` argument to specify the type of display.

```
usage: moderator.py [-h] [-g | -t] [players [players ...]]

Othello Moderator

positional arguments:
  players

optional arguments:
  -h, --help       show this help message and exit
  -g, --graphical  Use a graphical UI
  -t, --terminal   Use a text-based UI
```

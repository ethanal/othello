# Othello Moderator

A Python 3 Othello moderator. AIs are submodules of the `players` module that contain an implementation the `Player` class. The class name must be the same as the module name (the filename without the .py extension) for it to be detected.

```
usage: moderator.py [-h] [-g | -t] [players [players ...]]

Othello Moderator

positional arguments:
  players

optional arguments:
  -h, --help       show this help message and exit
  -g, --graphical  Use a graphical display
  -t, --terminal   Use a text-based display
```

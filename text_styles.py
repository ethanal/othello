import os
import platform
import sys


def _style(code):
    def wrapper(string):
        if os.isatty(sys.stdout.fileno()) and platform.system() != "Windows":
            return "\033[{:02}m{}\033[00m".format(code, string)
        return string
    return wrapper

bold = _style(1)
light = _style(2)
underlined = _style(4)
blinking = _style(5)

black = _style(30)
red = _style(31)
green = _style(32)
yellow = _style(33)
blue = _style(34)
magenta = _style(35)
cyan = _style(36)
white = _style(37)

bg_black = _style(40)
bg_red = _style(41)
bg_green = _style(42)
bg_yellow = _style(43)
bg_blue = _style(44)
bg_magenta = _style(45)
bg_cyan = _style(46)
bg_white = _style(47)

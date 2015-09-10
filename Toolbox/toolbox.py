__author__ = 'casanova'

import textwrap
import os
import re


class TextColors:
    BOLD = '\033[1m'
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'

    def __init__(self):
        pass


def my_str(s):
    print "----> ", type(s)
    if type(s) == unicode:
        return s
    else:
        return str(s)


def yellow(s):
    return TextColors.YELLOW + s + TextColors.END


def green(s):
    return TextColors.GREEN + s + TextColors.END


def red(s):
    return TextColors.RED + s + TextColors.END


def bold(s):
    return TextColors.BOLD + s + TextColors.END


def print_as_paragraph(colorfunc, s):
    # Determine terminal width
    columns = os.popen('stty size', 'r').read().split()[1]

    # Determine indent for subsequent lines
    m = re.search("\w", s)
    indent = " " * m.start()

    # print
    print colorfunc(textwrap.fill(s, width=int(columns) - 2, subsequent_indent=indent))

    return


def offset_string(s, offset):
    news = ""
    for l in s.splitlines():
        news += " " * offset + l + "\n"
    return news


class CustomException(Exception):
    pass

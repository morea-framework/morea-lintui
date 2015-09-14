__author__ = 'casanova'

import textwrap
import os
import re


class TextColors:
    BOLD = '\033[1m'
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'

    def __init__(self):
        pass


def my_str(s):
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


def add_quotes(do_it, string):
    if not do_it:
        return string

    # Deal with multi-line scalar values
    if "\n" in string:
        prefix = "|\n"
        offset = "  "
    else:
        prefix = ""
        offset = ""

    # Figure out the quoting
    if ('"' not in string) and ("'" not in string):
        quotes = '"'
    elif '"' in string and "'" not in string:
        quotes = "'"
    elif "'" in string and '"' not in string:
        quotes = '"'
    else:
        quotes = ""

    # put the last quote right before the last (if any)
    (string, count) = re.subn("\n$", quotes, string)
    if count == 0:
        string += quotes

    # Add the prefix and quotes
    string = prefix + quotes + string

    # Deal with the offset for multi-line values
    new_string = ""
    for l in string.splitlines():
        new_string += offset + l + "\n"

    return new_string

#  Create a monitor that detects object changes
from weakref import WeakKeyDictionary
from cPickle import dumps


class ObjectMonitor:
    def __init__(self):
        self.objects = WeakKeyDictionary()

    def has_changed(self, obj):
        current_pickle = dumps(obj, -1)
        changed = False
        if obj in self.objects:
            changed = current_pickle != self.objects[obj]
        self.objects[obj] = current_pickle
        # print "File"  + obj.path + "has changed: " + str(changed)
        return changed

morea_file_monitor = ObjectMonitor()

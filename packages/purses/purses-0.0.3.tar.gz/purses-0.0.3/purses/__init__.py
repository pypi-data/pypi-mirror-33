#!/usr/bin/env python
import curses
from .controller import Controller
from .model import Model
from .view import View
from .userspace import default_bindings

def _start(df, bindings):
    stdscr = curses.initscr()
    stdscr.keypad(True)
    try:
        model = Model.load(df)
        controller = Controller(bindings, model, stdscr)
        controller.loop()
    except Exception:
        raise
    finally:
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        del stdscr

def load(tabular, bindings=None):
    """Load the tabular data into curses.

       The tabular data can be a filename to a csv file or a Pandas dataframe.
       Launches a curses view.

       The `bindings` argument is optional and can be a mapping from curses keys
       (e.g., 's', '2', or 'KEY_UP') to functions with signature

           function(df, row, col, nav, msg, user_input) -> df / None

       and if the return value is a dataframe, that will be the new dataframe.
       It is also possible to inplace manipulate df.  It is advisable that the
       signature is actually

           function(df, row, col, nav, msg, user_input, *args, **kwargs)

       to accommodate for future changes.

       The object `nav` has 9 functions: up, down, right, left, panup, pandown,
       panright, panleft, and to.  The function to(row, col) puts curser in
       given coord.

       The messenger, msg, is a function that takes a string and write the
       string to the message area.

       The user_input function is called to get input from user.  It is
       terminated by a newline, but that can be configured.

    """

    if bindings is None:
        bindings = default_bindings()

    if isinstance(tabular, str):
        import pandas as pd
        tabular = pd.read_csv(tabular)
    _start(tabular, bindings)

def main():
    from sys import argv
    if len(argv) != 2:
        exit('Usage: purses.py data/iris.csv')
    load(argv[1])

__version__ = '0.0.3'

#!/usr/bin/env python
import curses
from .controller import Controller
from .model import Model
from .view import View

def _start(df):
    stdscr = curses.initscr()
    stdscr.keypad(True)
    try:
        model = Model.load(df)
        controller = Controller(model, stdscr)
        controller.loop()
    except Exception:
        raise
    finally:
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        del stdscr

def load(df):
    if isinstance(df, str):
        import pandas as pd
        df = pd.read_csv(df)
    _start(df)

def main():
    from sys import argv
    if len(argv) != 2:
        exit('Usage: purses.py data/iris.csv')
    load(argv[1])

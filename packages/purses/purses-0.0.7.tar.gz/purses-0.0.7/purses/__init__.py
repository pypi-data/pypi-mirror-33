#!/usr/bin/env python
import curses  # for key bindings only

from .controller import Controller
from .model import Model

class summer:
    def __init__(self):
        self.sum_ = 0
    def add(self, getter, setter, cursor):
        self.sum_ += getter(*cursor)
    def flush(self, getter, setter, cursor):
        setter(self.sum_, *cursor)
        self.sum_ = 0

def printer(getter, setter, cursor):
    r,c = cursor
    if c >= 0:
        msg = '{}: {}'.format(cursor, getter(r,c))
    else:
        msg = '{}: (at index)'.format((r,c+1))
    print(msg)

def square(getter, setter, cursor):
    val = getter(*cursor)
    setter(val**2, *cursor)

def deleter(getter, setter, cursor):
    setter(float('inf'), *cursor)

def load(tabular, bindings=None):
    """Load the tabular data into curses.

       The tabular data can be a filename to a csv file or a Pandas dataframe.
       Launches a curses view.

    """

    name = ''
    if isinstance(tabular, str):
        import pandas as pd
        name = tabular
        tabular = pd.read_csv(tabular)
    model = Model(tabular, name)
    cntrl = Controller(model)
    autumn = summer()
    cntrl.add_handlers(
        {
            'p': printer,
            's': square,
            curses.KEY_DC: deleter,
            'a': autumn.add,
            'f': autumn.flush,
        }
    )
    cntrl.run()

def main():
    from sys import argv
    if len(argv) != 2:
        exit('Usage: purses.py data/iris.csv')
    load(argv[1])

if __name__ == '__main__':
    main()

__version__ = '0.0.7'

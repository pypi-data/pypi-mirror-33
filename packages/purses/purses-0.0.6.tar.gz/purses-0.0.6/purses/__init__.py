#!/usr/bin/env python

from .controller import Controller


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
    view = Controller(tabular, name)
    view.run()

def main():
    from sys import argv
    if len(argv) != 2:
        exit('Usage: purses.py data/iris.csv')
    load(argv[1])

if __name__ == '__main__':
    main()

__version__ = '0.0.6'

# Purses

Purses is a Pandas Curses program.

It allows you to jump into a curses view of any dataframe and edit the contents,
as well as open a Pandas dataframe from the command line with the purses command
line tool.

## Installation

Either run

* `pip install purses`
* `pip install git+https://github.com/pgdr/purses`
* or clone this repository to unlock new loot boxes

## Starting Purses

Purses can be used either as a terminal tool by running `purses myfile.csv`, or
from inside a Python shell.

```python
import purses
purses.load('myfile.csv')
```

You can also load a dataframe directly

```python
import purses
import pandas as pd
df = pd.read_csv('myfile.csv')
purses.load(df)
```

## Usage

Navigation in Purses is done via the `<UP>`/`<DOWN>`/`<RIGHT>`/`<LEFT>` keys.
To scroll (or pan) the view, use `C-<UP>`, `C-<DOWN>`, `C-<RIGHT>`, `C-<LEFT>`.

You can delete a cell by using the `<DEL>` key.

Inserting values into the current cell is currently limited to the integers 0-9,
and is done via typing `0` (or any other one-digit'd integer, resp.).

Quit Purses with `q`.


## Defining your own key bindings

Any sufficiently advanced tool supports programmatic tools bindings.

Any key press event can trigger a callback with the provided signature below,
however, it is advisable to add also `*args` and `**kwargs` to the function
parameter list to accomodate for future additions.

```python
function(df: pandas.DataFrame,
         row: int,
         col: int,
         nav: navigator,
         msg: messenger,
         user_input: user_input) -> DataFrame
```

If a key (e.g. `s`) is bound to the above `function`, everytime `s` is pressed,
`function` is called, with `df` being the dataframe in question, and `row` and
`col` the coordinates to the cursor's cell.

The `nav` object has nine functions, `up`, `down`, `left`, `right`, for moving
the cursor, as well as for panning (or scrolling) the view, `panup`, `pandown`,
`panleft`, `panright`.  Finally, it also has a function `to(row, col)` to move
to a specific cell.

The `msg` function can be given any string to display in the message area and
the `user_input` is used to get a string from the user.


If a none-None value is returned from the callback, it is assumed to be the new
dataframe, and the current dataframe is replaced with the returned dataframe.


### Some examples


#### Example:

```python
def log_cell_content(df, row, col, *args, **kwargs):
    with open('log', 'a') as out:
        out.write('{},{} contains {}'.format(row, col, df.iloc[row][col]))

purses.load(df, bindings={'l': log_cell_content})
```


#### Example with state:


```python

class summer:
    def __init__(self):
        self.sum_ = 0
    def add(self, df, row, col, nav, msg, *args, **kwargs):
        self.sum_ += df.iat[row, col]
        msg('Current sum: {}'.format(self.sum_))
    def flush(self, df, row, col, nav, msg, *args, **kwargs):
        df.iat[row, col] = self.sum_
        msg('Flushed: {}'.format(self.sum_))
        self.sum_ = 0

autumn = summer()
purses.load(df, bindings={'s': autumn.add, 'f': autumn.flush})
```

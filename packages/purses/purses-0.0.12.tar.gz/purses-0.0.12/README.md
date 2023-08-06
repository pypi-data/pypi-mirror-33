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

Quit Purses with `q`.



## Defining your own key bindings

Any sufficiently advanced tool supports programmatic tools bindings.

Any key press event can trigger a callback with the provided signature below,
however, it is advisable to add also `*args` and `**kwargs` to the function
parameter list to accomodate for future additions.

```python
function(model, nav, io)
```

If a key (e.g. `s`) is bound to the above `function`, everytime `s` is pressed,
`function` is called, with `model` containing accessors to the dataframe in
question.

The `nav` object has functions, `up`, `down`, `left`, `right`, for moving the
cursor.  It also has a function `to(row, col)` to move to a specific cell.
`nav` also holds `row` and `col` the coordinates to the cursor's cell.

The `io` object has a function `message` which can be given any string to
display in the message area and `user_input` is used to get a string from the
user.


### Some examples



```python

class summer:
    def __init__(self):
        self.sum_ = 0
    def add(self, model, nav, io, *args, **kwargs):
        self.sum_ += model.get()  # the coordinates are optional
        io.message('Current sum: {}'.format(self.sum_))
    def flush(self, model, nav, io, *args, **kwargs):
        model.set(self.sum_)
        io.message('Flushed: {}'.format(self.sum_))
        self.sum_ = 0

autumn = summer()
purses.load(df, bindings={'s': autumn.add, 'f': autumn.flush})
```


To _square_ the element of a cell, we can hook the key `2` to the squaring
function:

```python
@purses.binding('2')
def square(self, model, *args, **kwargs):
    model.set(model.get()**2)
```

Indeed, when using decorators to bind the key to a function, there is no reason
to hang on to the name, so the above could be implemented as
```python
@purses.binding('2')
def _(self, model, *args, **kwargs):
    model.set(model.get()**2)
```

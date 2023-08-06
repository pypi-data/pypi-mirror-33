"""Wrapper classes for callback functionality.

This file contains some classes that are used to wrap the controller and the
model into nicer functions for the callbacks.

"""

class callback_io(object):
    def __init__(self, status_area):
        self.status = status_area

    def user_input(self, message='Enter input: '):
        return 'Not supported'

    def message(self, message):
        if self.status:
            self.status.value = message
            self.status.display()

    def clear(self):
        pass
        #if self.status:
            #self.self.status.clear()


class callback_model(object):
    def __init__(self, nav, model, tbl):
        self._nav = nav
        self._model_ = model
        self._tbl = tbl

    @property
    def df(self):
        return self._model_.df

    def __len__(self):
        return len(self._model_.df)

    @property
    def rows(self):
        return len(self)

    @property
    def cols(self):
        return len(list(self._model_.df.index))

    def _to_row_col(self, row=None, col=None):
        if isinstance(row, tuple) and col is None:
            row, col = row
        if row is None:
            row = self._nav.row
        if col is None:
            col = self._nav.col
        return row, col

    def get(self, row=None, col=None):
        row, col = self._to_row_col(row, col)
        if col < 0:
            return self._model_.df.index[row]
        return self._model_.df.iat[row, col]

    def set(self, val, row=None, col=None):
        row, col = self._to_row_col(row, col)
        self._model_.df.iat[row, col] = val
        for idx, model_val in enumerate(list(self._model_.df.iloc[row])):
            self._tbl.values[row][idx + 1] = model_val


class callback_navigator(object):
    def __init__(self, model, tbl):
        self._model_ = model
        self._tbl = tbl

    @property
    def cursor(self):
        r, c = self._tbl.edit_cell
        if self._model_.show_index:
            return r, c - 1
        return r, c

    @property
    def row(self):
        return self.cursor[0]

    @property
    def col(self):
        return self.cursor[1]

    def up(self):
        self._tbl.h_move_line_up(1)

    def down(self):
        self._tbl.h_move_line_down(1)

    def left(self):
        self._tbl.h_move_cell_left(1)

    def right(self):
        self._tbl.h_move_cell_right(1)

    def to(self, row, col):
        # admittedly not necessary to have an O(n) time alg here
        while row < self.row:
            self.up()
        while row > self.row:
            self.down()
        while col < self.col:
            self.left()
        while col > self.col:
            self.right()

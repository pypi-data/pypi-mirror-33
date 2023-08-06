import npyscreen


class _io(object):
    def __init__(self):
        pass

    def user_input(self, message='Enter input: '):
        return 'Not supported'

    def message(self, message):
        print(message)

    def clear(self):
        pass


class _model(object):
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


class _navigator(object):
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

    def moveup(self):
        self._tbl.h_move_line_up(1)

    def movedown(self):
        self._tbl.h_move_line_down(1)

    def moveleft(self):
        self._tbl.h_move_cell_left(1)

    def moveright(self):
        self._tbl.h_move_cell_right(1)


class Controller(npyscreen.NPSApp):
    def __init__(self, model):
        self.model = model
        self.gui = None
        self.tbl = None
        self._handlers = {}
        self.nav = None  # navigator for callback
        self.getset = None  # get and set for callback
        self.io = None  # io for callback

    def _init_tbl(self):
        self.tbl = self.gui.add(
            npyscreen.GridColTitles,
            relx=4,
            rely=3,
            width=72,
            col_titles=self.model.columns)
        self.tbl.values = []
        for x in range(len(self.model)):
            self.tbl.values.append(self.model.row(x))

        # create navigator object
        self.nav = _navigator(self.model, self.tbl)
        self.getset = _model(self.nav, self.model, self.tbl)
        self.io = _io()

    def _handle_wrapper(self, func):
        def _handle(key):
            res = func(self.getset, self.nav, self.io)
            return res

        return _handle

    def add_handlers(self, hdl):
        for handler in hdl:
            self._handlers[handler] = self._handle_wrapper(hdl[handler])

    def main(self):
        self.gui = npyscreen.ActionFormMinimal(name=self.model.fname)
        self.gui.add_handlers(self._handlers)
        self._init_tbl()
        self.gui.edit()

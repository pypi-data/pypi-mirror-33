import npyscreen

class summer:
    def __init__(self):
        self.sum_ = 0
    def add(self, arg):
        print('add', arg)
    def flush(self, arg):
        print('flush', arg)


class Controller(npyscreen.NPSApp):
    def __init__(self, model):
        self.model = model
        self.gui = None
        self.tbl = None
        self._handlers = {}

    def _init_tbl(self):
        self.tbl = self.gui.add(npyscreen.GridColTitles,
                                relx=4,
                                rely=3,
                                width=72,
                                col_titles=self.model.columns)
        self.tbl.values=[]
        for x in range(len(self.model)):
            self.tbl.values.append(self.model.row(x))

    def _get_iat(self, row, col):
        if col < 0:
            return self.model.df.index[row]
        return self.model.df.iat[row, col]

    def _set_iat(self, val, row, col):
        self.model.df.iat[row, col] = val
        for idx, model_val in enumerate(list(self.model.df.iloc[row])):
            self.tbl.values[row][idx+1] = model_val

    @property
    def cursor(self):
        r,c = self.tbl.edit_cell
        if self.model.show_index:
            return r, c-1
        return r, c

    def _handle_wrapper(self, func):
        def _handle(key):
            res = func(self._get_iat, self._set_iat, self.cursor)
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

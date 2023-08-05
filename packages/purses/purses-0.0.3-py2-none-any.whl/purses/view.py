import curses

CELL_WIDTH = 3 + 1 + 5 # 123.12345
PADDING = 5 # to accomodate ' | '

PADDING_TOP = 4
PADDING_BOT = 3

class View(object):

    def __init__(self, scr, rows, cols, mock=False):
        self.scr = scr
        self._top = self._left = 0
        self._row = self._col = 0  # relative index to _top and _left
        self._cols = cols
        self._rows = rows
        if not mock:
            self.pad = curses.newpad(rows, cols*(CELL_WIDTH + PADDING))

        self.col_index = scr.subwin(PADDING_TOP, 3)
        self.header = scr.subwin(3, 10)
        self.cols = [scr.subwin(PADDING_TOP, (CELL_WIDTH+PADDING-1)*(i+1)) for i in range(cols)]

    def moveup(self):
        self._row = max(0, self._row - 1)
    def movedown(self):
        self._row += 1
    def moveleft(self):
        self._col = max(0, self._col - 1)
    def moveright(self):
        self._col += 1

    def panup(self):
        self._top = max(0, self._top - 1)
        self.movedown()
    def pandown(self):
        self._top += 1
        self.moveup()
    def panleft(self):
        self._left = max(0, self._left - 1)
        self.moveright()
    def panright(self):
        self._left += 1
        self.moveleft()

    def to(self, row, col):
        self._row = max(0, min(row, self._rows))
        self._col = max(0, min(col, self._cols))
        self._top = self._row
        self._left = self._col

    def message(self, msg):
        if not isinstance(msg, str):
            msg = '{} [{}]'.format(msg, type(msg))
        self.scr.addstr(0, 0, msg, curses.A_BOLD)
        self.scr.refresh()

    @property
    def coords(self):
        """Return the index in the dataframe, that is the indices + pan."""
        return self._row + self._top, self._col + self._left

    def __grid_row_iter(self):
        for row in range(self._rows - PADDING_TOP - PADDING_BOT):
            yield row

    def _draw_index(self, model):
        self.col_index.clear()
        for y in self.__grid_row_iter():
            self.col_index.addstr(y, 0, '{}'.format(model.df.index[y+self._top]).rjust(PADDING))
        self.col_index.refresh()

    def __attr_cell(self, row, col):
        return curses.A_REVERSE if self.coords == (row, col) else curses.A_NORMAL

    def _draw_cols(self, model):
        for i in range(self._cols-1):
            self.cols[i].clear()
            for j in self.__grid_row_iter():
                entry = model.cell(j+self._top, i)
                entry = str(entry).rjust(CELL_WIDTH + PADDING - 1)
                self.cols[i].addstr(j, 0, entry, self.__attr_cell(j,i))
            self.cols[i].refresh()

    def _draw_header(self, model):
        self.header.clear()
        def fit_or_pad(head):
            head = head.rjust(CELL_WIDTH + PADDING - 1)
            if len(head) > CELL_WIDTH + PADDING:
                head = head[len(head) - (CELL_WIDTH + PADDING-1):]
            return head

        header = ''.join(map(fit_or_pad, model.df.columns))
        self.header.addstr(0, 0, header)
        self.header.refresh()

    def draw(self, model):
        self._draw_header(model)
        self._draw_index(model)
        self._draw_cols(model)

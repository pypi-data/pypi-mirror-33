import curses

CELL_WIDTH = 2 + 1 + 3 # 12.123
PADDING = 3 # to accomodate ' | '

class View(object):

    def __init__(self, scr, rows, cols, mock=False):
        self.scr = scr
        self._top = self._left = 0
        self._row = self._col = 0  # relative index to _top and _left
        self._cols = cols
        self._rows = rows
        if not mock:
            self.pad = curses.newpad(rows, cols*(CELL_WIDTH + PADDING))


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
    def pandown(self):
        self._top += 1
    def panleft(self):
        self._left = max(0, self._left - 1)
    def panright(self):
        self._left += 1

    def message(self, msg):
        if not isinstance(msg, str):
            msg = '{} [{}]'.format(msg, type(msg))
        self.scr.addstr(0, 0, msg, curses.A_BOLD)
        self.scr.refresh()

    @property
    def coords(self):
        """Return the index in the dataframe, that is the indices + pan."""
        return self._row + self._top, self._col + self._left

    def draw(self, model):
        for y in range(0, self._rows):
            for x in range(0, self._cols):
                entry = model.cell(y+self._top, x+self._left)
                entry = entry[:max(len(entry), CELL_WIDTH)]
                try:
                    if (y,x) == (self._row, self._col):
                        self.pad.addstr(y, (x*(CELL_WIDTH+PADDING)), entry, curses.A_REVERSE)
                    else:
                        self.pad.addstr(y, (x*(CELL_WIDTH+PADDING)), entry)
                except curses.error:
                    pass

        # 0,0 is topleft cell
        self.pad.refresh(0,0,5,5, 20,75)

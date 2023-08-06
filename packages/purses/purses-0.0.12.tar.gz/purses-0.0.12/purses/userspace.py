import curses
from .bindings import binding


class clipboard:
    def __init__(self):
        self.val = float('nan')

    def copy(self, model, nav, io, *args, **kwargs):
        self.val = model.get(nav.row, nav.col)
        io.message('copied {}'.format(self.val))

    def paste(self, model, nav, io, *args, **kwargs):
        model.set(self.val)
        io.message('paste {}'.format(self.val))

    def cut(self, model, nav, io, *args, **kwargs):
        self.copy(model, nav, io, *args, **kwargs)
        try:
            model.set(float('nan'))
        except ValueError:
            model.set(0)
        io.message('cut {}'.format(self.val))


_cb = clipboard()


@binding('c')
def _cp(model, nav, io, *args, **kwargs):
    _cb.copy(model, nav, io, *args, **kwargs)


@binding('v')
def _paste(model, nav, io, *args, **kwargs):
    _cb.paste(model, nav, io, *args, **kwargs)


@binding('x')
def _cut(model, nav, io, *args, **kwargs):
    _cb.cut(model, nav, io, *args, **kwargs)


@binding('i')
def cell_input(model, nav, io, *args, **kwargs):
    #inpt = io.user_input('Enter value to input: ')
    #try:
    #    inpt = float(inpt)
    #    df.iat[nav.row, nav.col] = inpt
    #except ValueError as err:
    #    io.message(err)
    pass


@binding('/')
def search(model, nav, io, *args, **kwargs):
    inpt = io.user_input('Search: ')
    inpt = 5.0
    srch = str(inpt).strip()
    for r in range(model.rows):
        for c in range(model.cols):
            val = str(model.get(r, c)).strip()
            if val == srch:
                print(r, c)
                return
    io.message('Did not find {srch}'.format(srch=srch))


class summer:
    def __init__(self):
        self.sum_ = 0

    def add(self, model, nav, io, *args, **kwargs):
        self.sum_ += model.get()
        io.message('Current sum: {}'.format(self.sum_))

    def flush(self, model, nav, io, *args, **kwargs):
        model.set(self.sum_)
        io.message('Flushed: {}'.format(self.sum_))
        self.sum_ = 0


autumn = summer()


@binding('s')
def _add(model, nav, io, *args, **kwargs):
    autumn.add(model, nav, io, *args, **kwargs)


@binding('f')
def _flush(model, nav, io, *args, **kwargs):
    autumn.flush(model, nav, io, *args, **kwargs)


def _live(M, i, j):
    def in_(coor):
        x, y = coor
        return 0 <= x < M.shape[0] and 0 <= y and y < M.shape[1]

    count = 0
    for r in range(-1, 2):
        for c in range(-1, 2):
            if c == r == 0:
                continue
            e = i + r, j + c
            if in_(e) and M[e[0]][e[1]] > 0:
                count += 1

    if M[i][j] == 1:
        return 2 <= count <= 3
    return 1 if count == 3 else 0


@binding('L')
def game_of_life(model, nav, io, *args, **kwargs):
    import copy
    G = model.df.values
    Gp = copy.deepcopy(G)
    s = G.shape
    for i in range(s[0]):
        for j in range(s[1]):
            Gp[i][j] = _live(G, i, j)
    for i in range(s[0]):
        for j in range(s[1]):
            model.set(Gp[i][j], i, j)

@binding('2')
def _(model, *args, **kwargs):
    model.set(model.get()**2)

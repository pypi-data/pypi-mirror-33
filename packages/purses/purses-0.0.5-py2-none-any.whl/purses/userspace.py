import curses

class clipboard:
    def __init__(self):
        self.val = float('nan')

    def copy(self, df, nav, io, *args, **kwargs):
        self.val = df.iat[nav.row, nav.col]
        io.message('copied {}'.format(self.val))

    def paste(self, df, nav, io, *args, **kwargs):
        df.iat[nav.row, nav.col] = self.val
        io.message('paste {}'.format(self.val))

    def cut(self, df, nav, io, *args, **kwargs):
        self.copy(df, nav, io, *args, **kwargs)
        df.iat[nav.row, nav.col] = float('nan')
        io.message('cut {}'.format(self.val))

def cell_input(df, nav, io, *args, **kwargs):
    inpt = io.user_input('Enter value to input: ')
    try:
        inpt = float(inpt)
        df.iat[nav.row, nav.col] = inpt
    except ValueError as err:
        io.message(err)

def search(df, nav, io, *args, **kwargs):
    inpt = io.user_input('Search: ')
    srch = str(inpt).strip()
    for r in range(len(df)):
        for c in range(len(df.iloc[r])):
            val = str(df.iat[r, c]).strip()
            if val == srch:
                nav.to(r, c)
                return
    io.message('Did not find {srch}'.format(srch=srch))

class summer:
    def __init__(self):
        self.sum_ = 0

    def add(self, df, nav, io, *args, **kwargs):
        self.sum_ += df.iat[nav.row, nav.col]
        io.message('Current sum: {}'.format(self.sum_))

    def flush(self, df, nav, io, *args, **kwargs):
        df.iat[nav.row, nav.col] = self.sum_
        io.message('Flushed: {}'.format(self.sum_))
        self.sum_ = 0


def live(M, i, j):
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


def game_of_life(df, nav, io, *args, **kwargs):
    import copy
    G = df.as_matrix()
    Gp = copy.deepcopy(G)
    s = G.shape
    highlight = {}
    for i in range(s[0]):
        for j in range(s[1]):
            Gp[i][j] = live(G, i, j)
    for i in range(s[0]):
        for j in range(s[1]):
            df.iat[i, j] = Gp[i][j]
            if Gp[i][j]:
                highlight[(i, j)] = curses.A_REVERSE
    return (None, highlight)


def default_bindings():
    autumn = summer()
    cp = clipboard()
    bindings = {'c': cp.copy, 'v': cp.paste, 'x': cp.cut,
                'i' : cell_input,
                '/' : search,
                's' : autumn.add, 'f': autumn.flush,
                '\n': game_of_life,
    }
    return bindings

class clipboard:
    def __init__(self):
        self.val = float('nan')
    def copy(self, df, row, col, nav, msg, *args, **kwargs):
        self.val = df.iat[row,col]
        msg('copied {}'.format(self.val))
    def paste(self, df, row, col, nav, msg, *args, **kwargs):
        df.iat[row, col] = self.val
        msg('paste {}'.format(self.val))
    def cut(self, df, row, col, nav, msg, *args, **kwargs):
        self.copy(df, row, col, nav, msg, *args, **kwargs)
        df.iat[row, col] = float('nan')
        msg('cut {}'.format(self.val))

def cell_input(df, row, col, nav, msg, user_input, *args, **kwargs):
    inpt = user_input('Enter value to input: ')
    try:
        inpt = float(inpt)
        df.iat[row, col] = inpt
    except ValueError as err:
        msg(err)

def search(df, row, col, nav, msg, user_input, *args, **kwargs):
    inpt = user_input('Search: ')
    srch = str(inpt).strip()
    for r in range(len(df)):
        for c in range(len(df.iloc[r])):
            val = str(df.iat[r, c]).strip()
            if val == srch:
                nav.to(r, c)
                return
    msg('Did not find {srch}'.format(srch=srch))

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


def game_of_life(df, row, col, nav, msg, *args, **kwargs):
    import copy
    G = df.as_matrix()
    Gp = copy.deepcopy(G)
    s = G.shape
    for i in range(s[0]):
        for j in range(s[1]):
            Gp[i][j] = live(G, i, j)
    for i in range(s[0]):
        for j in range(s[1]):
            df.iat[i, j] = Gp[i][j]


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

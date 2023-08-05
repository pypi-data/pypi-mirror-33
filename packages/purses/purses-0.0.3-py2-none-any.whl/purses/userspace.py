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

def default_bindings():
    cp = clipboard()
    bindings = {'c': cp.copy, 'v': cp.paste, 'x': cp.cut,
                'i' : cell_input,
                's' : search,
    }
    return bindings

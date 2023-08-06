class Model(object):
    def __init__(self, df, fname='Purses'):
        self.df = df
        self.fname = fname
        self.show_index = True

    @property
    def columns(self):
        if self.show_index:
            return [''] + list(self.df.columns)
        return list(self.df.columns)

    def row(self, r):
        if self.show_index:
            return [self.df.index[r]] + list(self.df.iloc[r])
        return list(self.df.iloc[r])

    def __len__(self):
        return len(self.df)

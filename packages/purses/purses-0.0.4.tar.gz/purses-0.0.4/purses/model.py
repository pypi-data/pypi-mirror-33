import pandas as pd

class Model(object):
    def __init__(self, df):
        self.df = df

    @staticmethod
    def load(df):
        return Model(df)

    @property
    def rows(self):
        return len(self.df)
    @property
    def columns(self):
        return len(self.df.columns)

    def insert(self, val, coords):
        row, col = coords
        self.df.iat[row, col] = val

    def _assert_index(self, row, col):
        y, x = row, col
        assert 0 <= y < self.rows, '0 <= {} < {}'.format(y, self.rows)
        assert 0 <= x < self.columns, '0 <= {} < {}'.format(x, self.columns)

    def delete(self, coords, nan=float('nan')):
        self.insert(nan, coords)

    def cell(self, row, col):
        y, x = row, col
        self._assert_index(y, x)
        r = list(self.df.iloc[y])
        cell = str(r[x])
        return cell

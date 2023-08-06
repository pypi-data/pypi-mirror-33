import npyscreen

class Controller(npyscreen.NPSApp):
    def __init__(self, df, fname='Purses'):
        self.fname = fname
        self.df = df
        self.gui = None
        self.tbl = None

    def _init_tbl(self):
        self.tbl = self.gui.add(npyscreen.GridColTitles,
                                relx=4,
                                rely=3,
                                width=72,
                                col_titles=['(idx)']+list(self.df.columns))
        self.tbl.values=[]
        for x in range(len(self.df)):
            self.tbl.values.append([self.df.index[x]] + list(self.df.iloc[x]))

    def main(self):
        self.gui = npyscreen.ActionFormMinimal(name=self.fname)
        self._init_tbl()
        self.gui.edit()

import npyscreen

from .callbackutil import callback_io, callback_navigator, callback_model

def _max_col_width(df):
    m = 4  # npyscreen.SimpleGrid does not like < 3, so 4 is safe
    m = max(m, max(map(len, map(str, list(df.columns)))))
    for c in df.columns:
        for e in df[c]:
            m = max(m, len(str(e)))
    return m

class Controller(npyscreen.NPSApp):
    def __init__(self, model):
        self.model = model
        self.gui = None
        self.tbl = None
        self.status = None
        self.description = None
        self._handlers = {}
        self.nav = None  # navigator for callback
        self.getset = None  # get and set for callback
        self.io = None  # io for callback


    def __widget_pos(self):
        # three widgets: description, table, status
        pos = {
            'description': {
                'max_height': 0,
                'relx': 4,
                'rely': 2,
            },
            'table': {
                'max_height': self.gui.lines - 5,
                'relx': 4,
                'rely': 2,
            },
            'status': {
                'max_height': 0,
                'relx': 4,
                'rely': -4,
            },
        }
        if self.gui.lines > 35: # large window, has both status and desc
            pos['description']['max_height'] = 10
            pos['status']['max_height'] = 2
            pos['table']['rely'] += 11
            pos['table']['max_height'] -= 13
        elif self.gui.lines > 25: # medium window, has only desc
            pos['description']['max_height'] = 10
            pos['table']['max_height'] -= 11
            pos['table']['rely'] += 11
        return pos

    def _init_tbl(self):
        pos = self.__widget_pos()

        ## Draw the description widget
        if pos['description']['max_height'] > 0:
            content = str(self.model.df.describe())
            self.description = self.gui.add(npyscreen.MultiLineEdit,
                                            value=content,
                                            editable=False,
                                            **pos['description'])
            self.description.set_editable(False)


        ## Draw the status widget
        if pos['status']['max_height'] > 0:
            content = 'Status'
            self.status = self.gui.add(npyscreen.MultiLineEdit,
                                       value=content,
                                       hidden=False,
                                       editable=False,
                                       **pos['status'])


        ## Draw the table widget (always)
        self.tbl = self.gui.add(npyscreen.GridColTitles,
                                width=72,
                                column_width=_max_col_width(self.model.df),
                                col_titles=self.model.columns,
                                **pos['table'])
        self.tbl.values = []
        for x in range(len(self.model)):
            self.tbl.values.append(self.model.row(x))

        # create navigator object
        self.nav = callback_navigator(self.model, self.tbl)
        self.getset = callback_model(self.nav, self.model, self.tbl)
        self.io = callback_io(self.status)

    def _handle_wrapper(self, func):
        def _handle(key):
            res = func(self.getset, self.nav, self.io)
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

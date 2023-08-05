import curses
from .view import View

class Controller(object):
    def __init__(self, model, scr):
        self._shutdown = False
        self.model = model
        self.scr = scr
        height, width = scr.getmaxyx()
        self.view = View(scr,
                         min(height-2, self.model.rows),
                         min(width-5, self.model.columns+1)) # +1 due to index col

        def shutdown():
            self._shutdown = True

        def helptext():
            self.view.message('q for quit, DEL for delete, '
                              'UP/DOWN/RIGHT/LEFT to navigate, '
                              '0-9 to insert')

        self._controlling = {
            'q': shutdown,
            'h': helptext,
        }

        self._navigation = {
            'KEY_UP': self.view.moveup,
            'KEY_DOWN': self.view.movedown,
            'KEY_RIGHT': self.view.moveright,
            'KEY_LEFT': self.view.moveleft,
            # moving view:
            'kUP5': self.view.panup,
            'kDN5': self.view.pandown,
            'kRIT5': self.view.panright,
            'kLFT5': self.view.panleft,
        }

        helptext()

        def __insert(model, i):
            return lambda: model.insert(i, self.view.coords)

        def __delete(model):
            return lambda: model.delete(self.view.coords)
        self._editing = {
            'KEY_DC': __delete(model),
        }
        self._editing.update(
            {'{}'.format(i) : __insert(model, i) for i in range(10)}
        )


    def _nav(self, key):
        if key in self._navigation:
            self._navigation[key]()
            return True
        return False

    def _editor(self, key):
        if key in self._editing:
            self._editing[key]()
            return True
        return False

    def _control(self, key):
        if key in self._controlling:
            self._controlling[key]()
            return True
        return False

    def message(self, msg):
        self.view.message(msg)

    def loop(self):
        while not self._shutdown:
            self.view.draw(self.model)
            user = self.scr.getkey()
            self.message(' '*100)  # clears previous message
            if self._nav(user):
                self.message(self.view.coords)
            elif self._editor(user):
                self.message(user)
            elif self._control(user):
                pass
            else:
                self.message('Unkown key {}'.format(user))

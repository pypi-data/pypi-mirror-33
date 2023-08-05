import curses
from .view import View

class _navigator:
    def __init__(self, view):
        self.view = view

    @property
    def row(self):
        return self.view.coords[0]

    @property
    def col(self):
        return self.view.coords[1]

    def up(self):
        self.view.moveup()
    def down(self):
        self.view.movedown()
    def left(self):
        self.view.moveleft()
    def right(self):
        self.view.moveright()

    def panup(self):
        self.view.panup()
    def pandown(self):
        self.view.pandown()
    def panleft(self):
        self.view.panleft()
    def panright(self):
        self.view.panright()

    def to(self, row, col):
        self.view.to(row, col)


class _io:
    def __init__(self, scr, view):
        self.scr = scr
        self.view = view
    def user_input(self, message='Enter input: ', terminator='\n'):
        user = ''
        self.clear()
        self.message(message)
        msg = []
        while user != terminator:
            msg.append(user)
            user = self.scr.getkey()
        self.clear()
        inpt = ''.join(msg)
        self.message('User input "{}"'.format(inpt))
        return inpt
    def message(self, message):
        self.view.message(message)
    def clear(self):
        self.message(' '*100)


class Controller(object):
    def __init__(self, bindings, model, scr):
        self._shutdown = False
        self.model = model
        self.scr = scr
        height, width = scr.getmaxyx()
        self.view = View(scr,
                         min(height-2, self.model.rows),
                         min(width-5, self.model.columns+1)) # +1 due to index col
        self.navigator = _navigator(self.view)
        self.io = _io(self.scr, self.view)

        self.__init_bindings(bindings)
        self.helptext()

    def __init_bindings(self, bindings):
        def __insert(val):
            def __f(df, nav, *args, **kwargs):
                df.iat[nav.row, nav.col] = val
            return __f

        def __delete(df, nav, *args, **kwargs):
            return __insert(float('nan'))(df, nav.row, nav.col)

        self._bindings = {
            # control
            'q': self.shutdown,
            'h': self.helptext,
            # navigate
            'KEY_UP': self.moveup,
            'KEY_DOWN': self.movedown,
            'KEY_RIGHT': self.moveright,
            'KEY_LEFT': self.moveleft,

            'kUP5': self.panup,
            'kDN5': self.pandown,
            'kRIT5': self.panright,
            'kLFT5': self.panleft,
            #
            'KEY_DC': __delete,
        }
        self._bindings.update(
            {'{}'.format(i) : __insert(i) for i in range(10)}
        )
        self._bindings.update(bindings)


    def shutdown(self, *args, **kwargs):  # ignore all args
        self._shutdown = True

    def helptext(self, *args, **kwargs):
        self.io.message('q for quit, DEL for delete, '
                        'UP/DOWN/RIGHT/LEFT to navigate, '
                        '0-9 to insert')

    def moveup(self, *args, **kwargs):
        self.navigator.up()
    def movedown(self, *args, **kwargs):
        self.navigator.down()
    def moveleft(self, *args, **kwargs):
        self.navigator.left()
    def moveright(self, *args, **kwargs):
        self.navigator.right()

    def panup(self, *args, **kwargs):
        self.navigator.panup()
    def pandown(self, *args, **kwargs):
        self.navigator.pandown()
    def panleft(self, *args, **kwargs):
        self.navigator.panleft()
    def panright(self, *args, **kwargs):
        self.navigator.panright()

    def _do_callback(self, user_key):
        callback_args = (self.model.df,
                         self.navigator,
                         self.io,
        )
        res = self._bindings[user_key](*callback_args)
        if res:
            if res[0] is not None:
                self.model.df = res[0]
            if res[1]:
                return res[1]
        return {}

    def loop(self):
        highlight = {}
        while not self._shutdown:
            with open('log', 'a') as f:
                f.write(str(highlight))
                f.write('\n')
            self.view.draw(self.model, highlight)

            user = self.scr.getkey()
            self.io.clear()
            if user in self._bindings:
                highlight = self._do_callback(user)
            else:
                self.io.message('Unkown key {}'.format(user))

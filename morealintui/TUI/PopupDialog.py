import urwid

from Toolbox.toolbox import CustomException

__author__ = 'casanova'


class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with nothing but a close button """
    signals = ['close']

    def __init__(self, msg, tui):
        self.tui = tui
        close_button = urwid.Button(">OK")
        urwid.connect_signal(close_button, 'click',
                             self.close_me)
        pile = urwid.Pile([urwid.AttrWrap(urwid.Text("Can't save due to the following:\n" + msg), 'error'),
                           urwid.Columns([(10, urwid.Text(" ")), (
                               10, urwid.AttrWrap(close_button, 'truefalse not selected', 'truefalse selected'))])])
        fill = urwid.Filler(pile)
        super(PopUpDialog, self).__init__(urwid.AttrWrap(fill, 'popbg'))

    def close_me(self, widget):
        self.tui.a_pop_up_is_opened = False
        self._emit("close")


class HiddenPopupLauncher(urwid.PopUpLauncher):
    def __init__(self, tui, viewframe):
        self.tui = tui
        self.viewframe = viewframe
        self.popup_message = ""
        urwid.PopUpLauncher.__init__(self, urwid.Button(""))

    def create_pop_up(self):
        pop_up = PopUpDialog(self.popup_message, self.tui)
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def open_the_pop_up(self, button):

        try:
            self.viewframe.save_content()
        except CustomException as e:
            self.popup_message = str(e)
            self.tui.a_pop_up_is_opened = True
            self.open_pop_up()
            return

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': -10, 'overlay_width': 70, 'overlay_height': 15}

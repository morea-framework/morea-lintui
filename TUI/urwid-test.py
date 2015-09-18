import time

__author__ = 'casanova'

import urwid

# urwid customization
urwid.Button.button_right = urwid.Text("")
urwid.Button.button_left = urwid.Text("")


class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with nothing but a close button """
    signals = ['close']

    def __init__(self):
        close_button = urwid.Button("that's pretty cool")

        urwid.connect_signal(close_button, 'click',
                             lambda button: self._emit("close"))
        pile = urwid.Pile([urwid.Text(
            "^^  I'm attached to the widget that opened me. "
            "^^  I'm attached to the widget that opened me. "
            "^^  I'm attached to the widget that opened me.     "
            "Try resizing the window!\n"), close_button])
        fill = urwid.Filler(pile)
        stuff = urwid.LineBox(fill)
        super(PopUpDialog, self).__init__(urwid.AttrWrap(stuff, 'popbg'))


class ThingWithAPopUp(urwid.PopUpLauncher):
    def __init__(self, mainframe):
        self.mainframe = mainframe
        super(ThingWithAPopUp, self).__init__(urwid.Button("click-me"))
        urwid.connect_signal(self.original_widget, 'click',
                             self.mainframe.some_function, None)

    def open_the_popup(self):
        time.sleep(10)
        self.open_pop_up()

    def create_pop_up(self):
        pop_up = PopUpDialog()
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 20}


class MainFrame(urwid.Pile):
    def __init__(self, string, num):
        row_list = []

        # Create a row with a popup
        self.thingwithapopup = ThingWithAPopUp(self)
        row_list.append(urwid.Columns([self.thingwithapopup]))

        super(MainFrame, self).__init__(row_list)

    def some_function(self, button):
        print "IN SOME FUNCTION.. stuff =", button
        self.thingwithapopup.open_the_popup()

# Set up our color scheme
palette = [
    ('titlebar', 'black', 'white'),
    ('refresh button', 'dark green,bold', 'black'),
    ('module button', 'dark green,bold', ''),
    ('outcome button', 'dark green,bold', ''),
    ('reading button', 'dark green,bold', ''),
    ('experience button', 'dark green,bold', ''),
    ('assessment button', 'dark green,bold', ''),
    ('button normal', 'light gray', '', 'standout'),
    ('button select', 'white', 'dark green'),
    ('quit button', 'dark red,bold', ''),
    ('exit button', 'dark red,bold', ''),
    ('getting quote', 'dark blue', 'black')]

# Create the "RANDOM QUOTES" header
header_text = urwid.Text(u'RANDOM QUOTES')
header = urwid.AttrMap(header_text, 'titlebar')


# Create the module Frames
main_frame = MainFrame("hello", 4)

quote_filler = urwid.Filler(main_frame, valign='top', top=1, bottom=1)
v_padding = urwid.Padding(quote_filler, left=1, right=1)
quote_box = urwid.LineBox(v_padding)
# Assemble the widgets into the widget layout
layout = urwid.Frame(header=None, body=quote_box, footer=None)

# Create the event loop
main_loop = urwid.MainLoop(layout, pop_ups=True, palette=palette)

# Kick off the program
main_loop.run()

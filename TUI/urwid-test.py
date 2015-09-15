import time

__author__ = 'casanova'

import urwid

class TrueFalseCheckBox(urwid.CheckBox):
    def __init__(self, label, state=False, has_mixed=False, on_state_change=None, user_data=None):
        self.states[True] =  urwid.SelectableIcon(u"[True ]")
        self.states[False] = urwid.SelectableIcon(u"[False]")
        super(TrueFalseCheckBox, self).__init__(label, state, has_mixed, on_state_change, user_data)

# urwid customization
urwid.Button.button_right = urwid.Text("")
urwid.Button.button_left = urwid.Text("")

class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with nothing but a close button """
    signals = ['close']
    def __init__(self):
        close_button = urwid.Button("that's pretty cool")
        other_button = urwid.Button("OTHER")

        urwid.connect_signal(close_button, 'click',
                             lambda button:self._emit("close"))
        pile = urwid.Pile([urwid.Text(
            "^^  I'm attached to the widget that opened me. "
            "Try resizing the window!\n"), close_button, other_button])
        fill = urwid.Filler(pile)
        stuff = urwid.LineBox(fill)
        self.__super.__init__(urwid.AttrWrap(stuff, 'popbg'))


class ThingWithAPopUp(urwid.PopUpLauncher):
    def __init__(self):
        self.__super.__init__(urwid.Button("click-me"))
        urwid.connect_signal(self.original_widget, 'click',
                             lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = PopUpDialog()
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left':0, 'top':1, 'overlay_width':32, 'overlay_height':20}




class MainFrame(urwid.Pile):
    def __init__(self, string, num):

        row_list = []

        # Create a row with a text entry zone:
        trash_button = urwid.CheckBox("")
        text_entry = urwid.Edit(caption="morea_title: ", edit_text="whatever", multiline=False,
                                align="left", wrap="space", allow_tab="False")
        urwid.connect_signal(text_entry, 'change', self.something, "hello")
        row_list.append(urwid.Columns([(4,trash_button), text_entry]))

        # Create a row with a popup
        trash_button = urwid.CheckBox("")
        text_entry = urwid.Button("morea_summary")
        text_label = urwid.Text(' "Some description that...."')
        row_list.append(urwid.Columns([(4,trash_button), ThingWithAPopUp(), (10,text_label)]))

        # Create a row with a True/false
        text_entry = urwid.Button("morea_published")
        trash_button = TrueFalseCheckBox("")
        row_list.append(urwid.Columns([(14,text_entry), (10,trash_button)]))

        super(MainFrame, self).__init__(row_list)

    def something(self, text_entry, state, userdata):
        return

    def popupcallback(self):

        return



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
    ('popbg', 'black', 'light gray'),
    ('exit button', 'dark red,bold', ''),
    ('getting quote', 'dark blue', 'black')]

# Create the "RANDOM QUOTES" header
header_text = urwid.Text(u'RANDOM QUOTES')
header = urwid.AttrMap(header_text, 'titlebar')

# Create the menus
menu_top = urwid.Text([
    u' ', ('module button', u'M'), u'odules |',
    u' ', ('outcome button', u'O'), u'utcomes |',
    u' ', ('reading button', u'R'), u'eadings |',
    u' ', ('experience button', u'E'), u'xperiences |',
    u' ', ('assessment button', u'A'), u'ssessments'])

menu_bottom = urwid.Text([
    u' ', ('quit button', u'Q'), u'uit & save |',
    u' e', ('exit button', u'X'), u'it'])


# Create the module Frames
main_frame = MainFrame("hello", 4)

# noinspection PyDictCreation
frame_dict = {}
frame_dict["modules"] = MainFrame("MODULES", 3)
frame_dict["outcomes"] = MainFrame("OUTCOMES", 4)
frame_dict["readings"] = MainFrame("READINGS", 5)
frame_dict["experiences"] = MainFrame("EXPERIENCES", 2)
frame_dict["assessments"] = MainFrame("ASSESSMENTS", 10)

quote_filler = urwid.Filler(main_frame, valign='top', top=1, bottom=1)
v_padding = urwid.Padding(quote_filler, left=1, right=1)
quote_box = urwid.LineBox(v_padding)
# Assemble the widgets into the widget layout
layout = urwid.Frame(header=menu_top, body=quote_box, footer=menu_bottom)


# Handle key presses
def handle_input(key):
    if key == 'M' or key == 'm':
        quote_filler.set_body(frame_dict["modules"])
        main_loop.draw_screen()
    elif key == 'O' or key == 'o':
        quote_filler.set_body(frame_dict["j"])
        main_loop.draw_screen()
    elif key == 'R' or key == 'r':
        quote_filler.set_body(frame_dict["readings"])
        main_loop.draw_screen()
    elif key == 'E' or key == 'e':
        quote_filler.set_body(frame_dict["experiences"])
        main_loop.draw_screen()
    elif key == 'A' or key == 'a':
        quote_filler.set_body(frame_dict["assessments"])
        main_loop.draw_screen()
    elif key == 'X' or key == 'x':
        raise urwid.ExitMainLoop()
    elif key == 'Q' or key == 'q':
        raise urwid.ExitMainLoop()

# Create the event loop
main_loop = urwid.MainLoop(layout, pop_ups=True, palette=palette, unhandled_input=handle_input)

# Kick off the program
main_loop.run()

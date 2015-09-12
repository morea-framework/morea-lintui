__author__ = 'casanova'

import urwid

# URWID customization
urwid.Button.button_right = urwid.Text("")
urwid.Button.button_left = urwid.Text("")


class MainFrame(urwid.Columns):
    def __init__(self, string, num):
        list_of_buttons = [urwid.Button(string + "_" + str(i)) for i in xrange(0, num)]
        widget_list = [urwid.Pile(list_of_buttons),
                       urwid.CheckBox("", state=False), urwid.CheckBox("")]

        # widget_list = [urwid.Pile([urwid.Button(string + "1", ), urwid.Button(string + "2")]),
        #               urwid.CheckBox("", state=False), urwid.CheckBox("")]
        super(MainFrame, self).__init__(widget_list)


# Set up our color scheme
palette = [
    ('titlebar', 'black', 'white'),
    ('refresh button', 'dark green,bold', 'black'),
    ('module button', 'dark green,bold', ''),
    ('outcome button', 'dark green,bold', ''),
    ('reading button', 'dark green,bold', ''),
    ('experience button', 'dark green,bold', ''),
    ('assessment button', 'dark green,bold', ''),
    ('quit button', 'dark red,bold', ''),
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
main_frame = MainFrame("hello",4)

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
    elif key == 'W' or key == 'w':
        frame_dict["outcomes"] = MainFrame("NEWOUTCOMES")
        main_loop.draw_screen()
    elif key == 'X' or key == 'x':
        raise urwid.ExitMainLoop()
    elif key == 'Q' or key == 'q':
        raise urwid.ExitMainLoop()


# Create the event loop
main_loop = urwid.MainLoop(layout, palette, unhandled_input=handle_input)

# Kick off the program
main_loop.run()

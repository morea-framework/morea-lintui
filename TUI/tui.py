import copy
import urwid

__author__ = 'casanova'
import curses

import urwid

class TopLevelFrame(urwid.Pile):

    def __init__(self, _tui):
        self.tui = _tui


class TUI:

    def __init__(self, morea_content):

        self.content = morea_content

        # URWID customizations (could break in future versions of URWID)
        urwid.Button.button_right = urwid.Text("")
        urwid.Button.button_left = urwid.Text("")

        # Color palette
        self.palette = [
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

        # Create the top menu
        self.menu_top = urwid.Text([
            u' ', ('module button', u'M'), u'odules |',
            u' ', ('outcome button', u'O'), u'utcomes |',
            u' ', ('reading button', u'R'), u'eadings |',
            u' ', ('experience button', u'E'), u'xperiences |',
            u' ', ('assessment button', u'A'), u'ssessments'])

        # Create the bottom menu
        self.menu_bottom = urwid.Text([
            u' ', ('quit button', u'Q'), u'uit & save |',
            u' e', ('exit button', u'X'), u'it'])


        # Create all top-level frames
        top_level_frame_dict = {}
        top_level_frame_dict["modules"] = TopLevelFrame()
        top_level_frame_dict["outcomes"] = TopLevelFrame()
        top_level_frame_dict["readings"] = TopLevelFrame()
        top_level_frame_dict["experiences"] = TopLevelFrame()
        top_level_frame_dict["assessments"] = TopLevelFrame()

        BARF  BARF BARF

quote_filler = urwid.Filler(main_frame, valign='top', top=1, bottom=1)
v_padding = urwid.Padding(quote_filler, left=1, right=1)
quote_box = urwid.LineBox(v_padding)
# Assemble the widgets into the widget layout
layout = urwid.Frame(header=menu_top, body=quote_box, footer=menu_bottom)


# Create main loop
self.main_loop = urwid.MainLoop(XXXSOMEMAINTHINGXXX, self.palette, unhandled_input=handle_input)

return


def launch(self):
    self.main_loop.run()
    # TODO: do something?




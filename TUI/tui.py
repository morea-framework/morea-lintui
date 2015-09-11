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
        menu_top = urwid.Text([
            u' ', ('module button', u'M'), u'odules |',
            u' ', ('outcome button', u'O'), u'utcomes |',
            u' ', ('reading button', u'R'), u'eadings |',
            u' ', ('experience button', u'E'), u'xperiences |',
            u' ', ('assessment button', u'A'), u'ssessments'])

        # Create the bottom menu
        menu_bottom = urwid.Text([
            u' ', ('quit button', u'Q'), u'uit & save |',
            u' e', ('exit button', u'X'), u'it'])

        # Create all top-level frames
        self.top_level_frame_dict = {}
        self.top_level_frame_dict["modules"] = TopLevelFrame()
        self.top_level_frame_dict["readings"] = TopLevelFrame()
        self.top_level_frame_dict["experiences"] = TopLevelFrame()
        self.top_level_frame_dict["assessments"] = TopLevelFrame()

        # Set up the main view
        self.frame_holder = urwid.Filler(self.top_level_frame_dict["modules"], valign='top', top=1, bottom=1)
        v_padding = urwid.Padding(self.frame_holder, left=1, right=1)
        line_box = urwid.LineBox(v_padding)
        # Assemble the widgets into the widget layout
        overall_layout = urwid.Frame(header=menu_top, body=line_box, footer=menu_bottom)
        self.main_loop = urwid.MainLoop(overall_layout, self.palette, unhandled_input=self.handle_key_strokes)
        return

    def handle_key_stroke(self, key):
        if key == 'M' or key == 'm':
            self.frame_holder.set_body(self.top_level_frame_dict["modules"])
            self.main_loop.draw_screen()
        elif key == 'O' or key == 'o':
            self.frame_holder.set_body(self.top_level_frame_dict["j"])
            self.main_loop.draw_screen()
        elif key == 'R' or key == 'r':
            self.frame_holder.set_body(self.top_level_frame_dict["readings"])
            self.main_loop.draw_screen()
        elif key == 'E' or key == 'e':
            self.frame_holder.set_body(self.top_level_frame_dict["experiences"])
            self.main_loop.draw_screen()
        elif key == 'A' or key == 'a':
            self.frame_holder.set_body(self.top_level_frame_dict["assessments"])
            self.main_loop.draw_screen()
        elif key == 'X' or key == 'x':
            raise urwid.ExitMainLoop()
        elif key == 'Q' or key == 'q':
            raise urwid.ExitMainLoop()


    def launch(self):
        self.main_loop.run()
        # TODO: do something?

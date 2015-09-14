import time
from Toolbox.toolbox import num_term_colors
from TopLevelFrame import TopLevelFrame

__author__ = 'casanova'

import urwid

class TUI(object):

    # noinspection PyDictCreation,PyDictCreation
    def __init__(self, morea_content):
        self.save = False
        self.content = morea_content

        # URWID customizations (could break in future versions of URWID)
        urwid.Button.button_right = urwid.Text("")
        urwid.Button.button_left = urwid.Text("")
        urwid.CheckBox.states[True] = urwid.SelectableIcon(u"[\u2715]")

        # Color palette

        # This is a hack because I can't get the %$#@#$ palette to work correctly
        # to handle different color modes
        if num_term_colors() == 256:
            self.palette = [
                ('top button key', 'dark green', 'dark gray', '', 'light gray', 'dark gray'),
                ('top button nonkey', 'white', 'dark gray', '', 'white', 'dark red'),
                ('bottom button key', 'dark red', 'dark gray', '', 'light gray', 'dark gray'),
                ('bottom button nonkey', 'white', 'dark gray', '', 'white', 'dark gray'),
                ('body', 'white', 'dark gray', '', 'white', 'dark gray'),
                ('topframe not selected', 'white', 'dark gray', '', 'white', 'dark gray'),
                ('topframe selected', 'brown, standout', 'dark gray', '', 'yellow, standout', 'dark gray'),
                ('header', 'white, bold', 'dark gray', '', 'white, bold', 'dark gray'),
            ]
        else:
            self.palette = [
                ('top button key', 'dark green', 'black', '', 'light gray', 'dark gray'),
                ('top button nonkey', 'white', 'black', '', 'white', 'dark red'),
                ('bottom button key', 'dark red', 'black', '', 'light gray', 'dark gray'),
                ('bottom button nonkey', 'white', 'black', '', 'white', 'dark gray'),
                ('body', 'white', 'black', '', 'white', 'dark gray'),
                ('topframe not selected', 'white', 'black', '', 'white', 'dark gray'),
                ('topframe selected', 'brown, standout', 'black', '', 'yellow, standout', 'dark gray'),
                ('header', 'white, bold', 'black', '', 'white, bold', 'dark gray'),
            ]

        # Create the top menu
        menu_top = urwid.Text([
            u' ', ('top button key', u'M'), ('top button nonkey',u'odules'), ' |',
            u' ', ('top button key', u'O'), u'utcomes |',
            u' ', ('top button key', u'R'), u'eadings |',
            u' ', ('top button key', u'E'), u'xperiences |',
            u' ', ('top button key', u'A'), u'ssessments'])

        # Create the bottom menu
        menu_bottom = urwid.Text([
            u' ', ('bottom button key', u'Q'), ('bottom button nonkey', u'uit & save |'),
            ('bottom button nonkey',u' e'), ('bottom button key', u'X'), ('bottom button nonkey', u'it')])

        # Create all top-level frames
        self.top_level_frame_dict = {}
        self.create_module_top_level_frame()
        self.create_outcomes_top_level_frame()
        self.create_readings_top_level_frame()
        self.create_experiences_top_level_frame()
        self.create_assessments_top_level_frame()

        # Set up the main view
        self.frame_holder = urwid.Filler(self.top_level_frame_dict["modules"], valign='top', top=1, bottom=1)
        v_padding = urwid.Padding(self.frame_holder, left=1, right=1)
        line_box = urwid.LineBox(v_padding)

        # Assemble the widgets into the widget layout
        overall_layout = urwid.AttrWrap(urwid.Frame(header=menu_top, body=line_box, footer=menu_bottom), 'body')
        self.main_loop = urwid.MainLoop(overall_layout, palette=self.palette, unhandled_input=self.handle_key_stroke)

        screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(256, True)

        return

    def create_module_top_level_frame(self, focus=None):
        self.top_level_frame_dict["modules"] = TopLevelFrame(self, ("module", "-- MODULES --"),
                                                             [("published", "publi\nshed"),
                                                              ("morea_coming_soon", "coming\nsoon"),
                                                              ("morea_highlight", "high\nlight")],
                                                             sorting=True, focus=focus)

    def create_outcomes_top_level_frame(self):
        self.top_level_frame_dict["outcomes"] = TopLevelFrame(self, ("outcome", "-- OUTCOMES  --"), [])

    def create_readings_top_level_frame(self):
        self.top_level_frame_dict["readings"] = TopLevelFrame(self, ("reading", "-- READINGS --"), [])

    def create_experiences_top_level_frame(self):
        self.top_level_frame_dict["experiences"] = TopLevelFrame(self, ("experience", "-- EXPERIENCES --"), [])

    def create_assessments_top_level_frame(self):
        self.top_level_frame_dict["assessments"] = TopLevelFrame(self, ("assessment", "-- ASSESSMENTS --"), [])

    def handle_key_stroke(self, key):
        if key == 'M' or key == 'm':
            self.frame_holder.set_body(self.top_level_frame_dict["modules"])
            self.main_loop.draw_screen()
        elif key == 'O' or key == 'o':
            self.frame_holder.set_body(self.top_level_frame_dict["outcomes"])
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
            self.save = False
            raise urwid.ExitMainLoop()
        elif key == 'Q' or key == 'q':
            self.save = True
            raise urwid.ExitMainLoop()

    # noinspection PyMethodMayBeStatic
    def handle_moreaid_button_press(self, button, user_data):
        return

    # noinspection PyUnusedLocal
    def handle_module_sorting_button_press(self, button, user_data):
        (direction, f) = user_data
        self.content.update_file_sort_order(f, direction)

        # Regenerate the module frame, with the correct focus
        self.create_module_top_level_frame(focus=("sorting", direction, f))
        self.frame_holder.set_body(self.top_level_frame_dict["modules"])
        self.main_loop.draw_screen()
        return

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def handle_toplevelframe_checkbox_state_change(self, cb, state, user_data):
        (f, property_key) = user_data
        f.set_value_of_scalar_property(property_key, state)
        return

    def launch(self):
        self.main_loop.run()
        if self.save:
            return self.content
        else:
            return None

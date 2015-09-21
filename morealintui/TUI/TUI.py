from ViewFrame import ViewFrame
from Toolbox.toolbox import num_term_colors, CustomException
from TopLevelFrame import TopLevelFrame, FocusRememberingButton, FocusRememberingCheckBox

__author__ = 'casanova'

import urwid


class TUI(object):
    # noinspection PyDictCreation,PyDictCreation
    def __init__(self, morea_content):
        self.save = False
        self.content = morea_content

        self.a_pop_up_is_opened = False

        # URWID customizations (could break in future versions of URWID)
        urwid.Button.button_right = urwid.Text("")
        urwid.Button.button_left = urwid.Text("")
        urwid.CheckBox.states[True] = urwid.SelectableIcon(u"[\u2715]")

        # Color palette

        # This is a hack because I can't get the %$#@#$ palette to work correctly
        # to handle different color modes
        if num_term_colors() == 256:
            self.palette = [
                ('top button key', 'dark green', 'black', '', 'light gray', 'black'),
                ('top button nonkey', 'white', 'black', '', 'white', 'dark red'),
                ('bottom button key', 'dark red', 'black', '', 'light gray', 'black'),
                ('bottom button nonkey', 'white', 'black', '', 'white', 'black'),
                ('body', 'white', 'black', '', 'white', 'black'),
                ('error', 'dark red', 'light gray'),
                ('dull', 'dark blue', 'black'),
                ('duller', 'dark green', 'black'),
                ('commentout button', 'dark red', 'black'),
                ('topframe not selected', 'white', 'black', '', 'white', 'black'),
                ('topframe selected', 'yellow, standout', 'black', '', 'yellow, standout', 'black'),
                ('truefalse not selected', 'white', 'black', '', 'white', 'black'),
                ('popbg', 'black', 'light gray'),
                ('truefalse selected', 'standout', 'black', '', 'standout', 'black'),
                ('header', 'white, bold', 'black', '', 'white, bold', 'black'),
            ]
        else:
            self.palette = [
                ('top button key', 'dark green', 'black', '', 'light gray', 'black'),
                ('top button nonkey', 'white', 'black', '', 'white', 'dark red'),
                ('bottom button key', 'dark red', 'black', '', 'light gray', 'black'),
                ('bottom button nonkey', 'white', 'black', '', 'white', 'black'),
                ('body', 'white', 'black', '', 'white', 'black'),
                ('error', 'dark red', 'light gray'),
                ('dull', 'dark blue', 'black'),
                ('duller', 'dark green', 'black'),
                ('commentout button', 'dark red', 'black'),
                ('topframe not selected', 'white', 'black', '', 'white', 'black'),
                ('topframe selected', 'yellow, standout', 'black', '', 'yellow, standout', 'black'),
                ('truefalse not selected', 'white', 'black', '', 'white', 'black'),
                ('truefalse selected', 'standout', 'black', '', 'standout', 'black'),
                ('header', 'white, bold', 'black', '', 'white, bold', 'black'),
            ]

        # Create the top menu
        self.menu_top = urwid.Text([
            u' ', ('top button key', u'M'), ('top button nonkey', u'odules'), ' |',
            u' ', ('top button key', u'O'), u'utcomes |',
            u' ', ('top button key', u'R'), u'eadings |',
            u' ', ('top button key', u'E'), u'xperiences |',
            u' ', ('top button key', u'A'), u'ssessments'])

        self.menu_top_empty = urwid.Text("")

        # Create the bottom menu
        self.menu_bottom_toplevel = urwid.Text([
            u' ', ('bottom button key', u'Q'), ('bottom button nonkey', u'uit & save |'),
            ('bottom button nonkey', u' e'), ('bottom button key', u'X'), ('bottom button nonkey', u'it')])

        self.menu_bottom_viewframe = urwid.Text([
            u' ', ('bottom button key', u'C'), ('bottom button nonkey', u'ancel |'),
            u' ', ('bottom button key', u'S'), ('bottom button nonkey', u'ave')])

        # Create all top-level frames
        self.top_level_frame_dict = {}
        self.generate_all_top_level_frames()

        # Set up the main view
        self.frame_holder = urwid.Filler(self.top_level_frame_dict["module"], valign='top', top=1, bottom=1)
        v_padding = urwid.Padding(self.frame_holder, left=1, right=1)
        line_box = urwid.LineBox(v_padding)

        # Assemble the widgets into the widget layout
        self.main_frame = urwid.Frame(header=self.menu_top, body=line_box, footer=self.menu_bottom_toplevel)
        self.overall_layout = urwid.AttrWrap(self.main_frame, 'body')
        self.main_loop = urwid.MainLoop(self.overall_layout, pop_ups=True, palette=self.palette,
                                        unhandled_input=self.handle_key_stroke)

        screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(256, True)

        return

    def generate_all_top_level_frames(self):
        self.create_modules_top_level_frame()
        self.create_outcomes_top_level_frame()
        self.create_readings_top_level_frame()
        self.create_experiences_top_level_frame()
        self.create_assessments_top_level_frame()

    def create_modules_top_level_frame(self):

        if "module" in self.top_level_frame_dict:
            focus_memory = get_focus_memory(self.top_level_frame_dict["module"].get_focus_widgets()[-1])
        else:
            focus_memory = None
        self.top_level_frame_dict["module"] = TopLevelFrame(self, ("module", "-- MODULES --"),
                                                            [("published", "publi\nshed"),
                                                             ("morea_coming_soon", "coming\nsoon"),
                                                             ("morea_highlight", "high\nlight")],
                                                            sorting=True, focus_memory=focus_memory)

    def create_outcomes_top_level_frame(self):
        if "outcome" in self.top_level_frame_dict:
            focus_memory = get_focus_memory(self.top_level_frame_dict["outcome"].get_focus_widgets()[-1])
        else:
            focus_memory = None
        self.top_level_frame_dict["outcome"] = TopLevelFrame(self, ("outcome", "-- OUTCOMES  --"), [], sorting=True,
                                                             focus_memory=focus_memory)

    def create_readings_top_level_frame(self):
        if "reading" in self.top_level_frame_dict:
            focus_memory = get_focus_memory(self.top_level_frame_dict["reading"].get_focus_widgets()[-1])
        else:
            focus_memory = None
        self.top_level_frame_dict["reading"] = TopLevelFrame(self, ("reading", "-- READINGS --"), [],
                                                             sort_by_module_reference=True, focus_memory=focus_memory)

    def create_experiences_top_level_frame(self):
        if "experience" in self.top_level_frame_dict:
            focus_memory = get_focus_memory(self.top_level_frame_dict["experience"].get_focus_widgets()[-1])
        else:
            focus_memory = None
        self.top_level_frame_dict["experience"] = TopLevelFrame(self, ("experience", "-- EXPERIENCES --"), [],
                                                                sort_by_module_reference=True,
                                                                focus_memory=focus_memory)

    def create_assessments_top_level_frame(self):
        if "assessment" in self.top_level_frame_dict:
            focus_memory = get_focus_memory(self.top_level_frame_dict["assessment"].get_focus_widgets()[-1])
        else:
            focus_memory = None
        self.top_level_frame_dict["assessment"] = TopLevelFrame(self, ("assessment", "-- ASSESSMENTS --"), [],
                                                                sort_by_module_reference=True,
                                                                focus_memory=focus_memory)

    def handle_key_stroke(self, key):

        if self.a_pop_up_is_opened:
            return

        if type(self.frame_holder.get_body()) == TopLevelFrame:
            if key == 'M' or key == 'm':
                self.frame_holder.set_body(self.top_level_frame_dict["module"])
                self.main_frame.set_footer(self.menu_bottom_toplevel)
                self.main_loop.draw_screen()
            elif key == 'O' or key == 'o':
                self.frame_holder.set_body(self.top_level_frame_dict["outcome"])
                self.main_frame.set_footer(self.menu_bottom_toplevel)
                self.main_loop.draw_screen()
            elif key == 'R' or key == 'r':
                self.frame_holder.set_body(self.top_level_frame_dict["reading"])
                self.main_frame.set_footer(self.menu_bottom_toplevel)
                self.main_loop.draw_screen()
            elif key == 'E' or key == 'e':
                self.frame_holder.set_body(self.top_level_frame_dict["experience"])
                self.main_frame.set_footer(self.menu_bottom_toplevel)
                self.main_loop.draw_screen()
            elif key == 'A' or key == 'a':
                self.frame_holder.set_body(self.top_level_frame_dict["assessment"])
                self.main_frame.set_footer(self.menu_bottom_toplevel)
                self.main_loop.draw_screen()
            elif key == 'X' or key == 'x':
                self.save = False
                raise urwid.ExitMainLoop()
            elif key == 'Q' or key == 'q':
                self.save = True
                raise urwid.ExitMainLoop()
            else:
                return
        elif type(self.frame_holder.get_body()) == ViewFrame:
            view_frame = self.frame_holder.get_body()
            if key == 'C' or key == 'c':
                self.frame_holder.set_body(self.top_level_frame_dict[
                                               view_frame.morea_file.get_value_of_scalar_property("morea_type")])
                self.main_frame.set_footer(self.menu_bottom_toplevel)
                self.main_frame.set_header(self.menu_top)
                self.main_loop.draw_screen()
                return
            elif key == 'S' or key == 's':
                try:
                    view_frame.save_content()
                except CustomException:
                    view_frame.popup_launcher.open_the_pop_up(None)
                    return
                # We brute-force re-generate all top-level frames
                self.generate_all_top_level_frames()
                self.frame_holder.set_body(self.top_level_frame_dict[
                                               view_frame.morea_file.get_value_of_scalar_property("morea_type")])
                self.main_frame.set_footer(self.menu_bottom_toplevel)
                self.main_frame.set_header(self.menu_top)
                self.main_loop.draw_screen()
                return
            else:
                return

    # noinspection PyMethodMayBeStatic
    def handle_moreaid_button_press(self, button, user_data):
        f = user_data
        self.frame_holder.set_body(ViewFrame(self, f))
        self.main_frame.set_footer(self.menu_bottom_viewframe)
        self.main_frame.set_header(self.menu_top_empty)
        self.main_loop.draw_screen()
        return

    # noinspection PyUnusedLocal
    def handle_module_sorting_button_press(self, button, user_data):
        (direction, f) = user_data

        self.content.update_file_sort_order(f, direction)

        if self.frame_holder.get_body() == self.top_level_frame_dict["module"]:
            # Regenerate the module frame, with the correct focus
            self.create_modules_top_level_frame()
            self.frame_holder.set_body(self.top_level_frame_dict["module"])
        elif self.frame_holder.get_body() == self.top_level_frame_dict["outcome"]:
            # Regenerate the outcome frame, with the correct focus
            self.create_outcomes_top_level_frame()
            self.frame_holder.set_body(self.top_level_frame_dict["outcome"])

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


def get_focus_memory(widget):
    if type(widget) == FocusRememberingButton:
        return widget.focus_memory
    elif type(widget) == FocusRememberingCheckBox:
        return widget.focus_memory
    elif type(widget) == urwid.Padding:
        return widget.original_widget.focus_memory
    else:
        raise CustomException("Internal Error: can't figure out focus memory for type: " + str(type(widget)))

__author__ = 'casanova'

import urwid


class TopLevelFrame(urwid.Pile):
    def __init__(self, _tui,
                 morea_type_key_and_nickname,
                 list_of_check_box_property_keys_and_nicknames,
                 sorting=False, focus=None):

        self.tui = _tui

        list_of_rows = []

        # Create the top row
        type_column_header = urwid.Text(('header', "  " + morea_type_key_and_nickname[1]))
        other_column_headers = [urwid.Padding(urwid.Text(('header', s)), align='center', width=len(s)) for (m, s) in
                                list_of_check_box_property_keys_and_nicknames]
        if sorting:
            sorting_header = [(2, urwid.Text("")), (2, urwid.Text(""))]
        else:
            sorting_header = []

        list_of_rows.append(urwid.Columns([type_column_header] +
                                          [(6, header) for header in other_column_headers] +
                                          sorting_header, dividechars=1))

        # Create a blank row
        list_of_rows.append(urwid.Columns([], dividechars=1))

        # Get the list of files
        filelist = self.tui.content.get_filelist_for_type(morea_type_key_and_nickname[0])

        # Sort the files (is morea_sort_order is not specified, then at the top)
        filelist.sort(key=lambda x: x.get_value_of_scalar_property("morea_sort_order"), reverse=False)

        row_count = 0
        for f in filelist:

            widget_list = []
            row_count += 1

            # Create the morea_id button
            if f.get_value_of_scalar_property("title") == "":
                button_label = f.get_value_of_scalar_property("morea_id")
            else:
                button_label = u"\u25BA " + f.get_value_of_scalar_property("morea_id") + \
                               "\n   (" + f.get_value_of_scalar_property("title") + ")" + \
                               str(f.get_value_of_scalar_property("morea_sort_order"))

            button = urwid.Button(button_label,
                                  on_press=self.tui.handle_moreaid_button_press,
                                  user_data=["edit", f])

            widget_list += [button]

            # Create list_of_checkboxes for required True/False fields
            list_of_centered_checkboxes = []
            for (k, n) in list_of_check_box_property_keys_and_nicknames:
                if f.get_value_of_scalar_property(k) is not None:
                    cb = urwid.CheckBox("",
                                        state=f.get_value_of_scalar_property(k),
                                        on_state_change=self.tui.handle_toplevelframe_checkbox_state_change,
                                        user_data=(f, k))
                    list_of_centered_checkboxes.append(urwid.Padding(cb, align='center', width=len(n) - 2))
                else:
                    list_of_centered_checkboxes.append(urwid.Text(""))

            widget_list += [(6, x) for x in list_of_centered_checkboxes]

            # Create the sorting buttons if needed
            if sorting:
                if f.get_value_of_scalar_property("morea_sort_order") is not None:
                    button_up = urwid.Button(u'\u25B2', on_press=self.tui.handle_module_sorting_button_press,
                                             user_data=[-1, f])
                    button_down = urwid.Button(u'\u25bC', on_press=self.tui.handle_module_sorting_button_press,
                                               user_data=[+1, f])
                else:
                    button_up = urwid.Text(" ")
                    button_down = urwid.Text(" ")

                widget_list += [(2, button_up), (2, button_down)]

            row = urwid.Columns(widget_list, dividechars=1)
            if focus is not None:
                (label, direction, focus_file) = focus
                if focus_file == f:
                    focus_row = row_count
                    if direction == +1:
                        # print "SETTING FOCUS!!!"
                        row.set_focus_column(len(widget_list) - 1)
                    else:
                        # print "SETTING FOCUS"
                        row.set_focus_column(len(widget_list) - 2)

            list_of_rows.append(urwid.AttrWrap(row, 'topframe_not_selected', 'topframe_selected'))

        # Add all the rows in the pile
        urwid.Pile.__init__(self, list_of_rows)

        if focus is not None:
            self._set_focus_position(focus_row + 1)


class TUI:
    # noinspection PyDictCreation,PyDictCreation
    def __init__(self, morea_content):
        self.save = False
        self.content = morea_content

        # URWID customizations (could break in future versions of URWID)
        urwid.Button.button_right = urwid.Text("")
        urwid.Button.button_left = urwid.Text("")
        urwid.CheckBox.states[True] = urwid.SelectableIcon(u"[\u2715]")

        # Color palette
        background_color = 'dark gray'
        self.palette = [
            ('top button', 'dark green,bold', background_color),
            ('topframe_not_selected', 'white', background_color),
            ('topframe_selected', 'yellow', background_color),
            ('body', 'white', background_color),
            ('bottom button', 'dark red,bold', background_color),
            ('header', 'bold', background_color),
        ]

        # Create the top menu
        menu_top = urwid.Text([
            u' ', ('top button', u'M'), u'odules |',
            u' ', ('top button', u'O'), u'utcomes |',
            u' ', ('top button', u'R'), u'eadings |',
            u' ', ('top button', u'E'), u'xperiences |',
            u' ', ('top button', u'A'), u'ssessments'])

        # Create the bottom menu
        menu_bottom = urwid.Text([
            u' ', ('bottom button', u'Q'), u'uit & save |',
            u' e', ('bottom button', u'X'), u'it'])

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
        self.main_loop = urwid.MainLoop(overall_layout, self.palette, unhandled_input=self.handle_key_stroke)
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

    def handle_moreaid_button_press(self, button, user_data):
        return

    def handle_module_sorting_button_press(self, button, user_data):
        (direction, f) = user_data
        self.content.update_file_sort_order(f, direction)

        # Regenerate the module frame, with the correct focus
        self.create_module_top_level_frame(focus=("sorting", direction, f))
        self.frame_holder.set_body(self.top_level_frame_dict["modules"])
        self.main_loop.draw_screen()
        return

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

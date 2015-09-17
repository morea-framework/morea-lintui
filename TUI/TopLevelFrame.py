import urwid
from Toolbox.toolbox import bound_string

__author__ = 'casanova'


class TopLevelFrame(urwid.Pile):
    def __init__(self, _tui,
                 morea_type_key_and_nickname,
                 list_of_check_box_property_keys_and_nicknames,
                 sorting=False, focus=None, sort_by_module_reference=False):

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

        # noinspection PyTypeChecker
        list_of_rows.append(urwid.Columns([type_column_header] +
                                          [(6, header) for header in other_column_headers] +
                                          sorting_header, dividechars=1))

        # Create a blank row
        list_of_rows.append(urwid.Columns([], dividechars=1))

        # Get the list of files
        filelist = self.tui.content.get_filelist_for_type(morea_type_key_and_nickname[0])

        if sort_by_module_reference:
            filelist = self.tui.content.get_sorted_files_by_referencing_module(morea_type_key_and_nickname[0])
        else:
            # Sort the files (is morea_sort_order is not specified, then at the top)
            filelist.sort(key=lambda xx: xx.get_value_of_scalar_property("morea_sort_order"), reverse=False)

        for f in filelist:
            if sort_by_module_reference and f is None:
                row = urwid.Columns([urwid.AttrWrap(urwid.Text("\nUNREFERENCED BY ANY MODULE:"), 'dull')])
            elif sort_by_module_reference and f.get_value_of_scalar_property("morea_type") == "module":
               row = urwid.Columns([urwid.AttrWrap(urwid.Text("\nREFERENCE BY MODULE '"+
                        f.get_value_of_scalar_property("morea_id")+"':"), 'dull')])
            else:
                row = self.create_row(f, list_of_check_box_property_keys_and_nicknames, sorting)
            list_of_rows.append(urwid.AttrWrap(row, 'topframe not selected', 'topframe selected'))

        # Create a blank row
        list_of_rows.append(urwid.Columns([urwid.Button("")], dividechars=1))

        # Add all the rows in the pile
        urwid.Pile.__init__(self, list_of_rows)

        # TODO: SET THE FOCUS
        # if focus is not None:
        #     (label, direction, focus_file) = focus
        #     if focus_file == f:
        #         focus_row = row_count
        #         if direction == +1:
        #             # print "SETTING FOCUS!!!"
        #             row.set_focus_column(len(widget_list) - 1)
        #         else:
        #             # print "SETTING FOCUS"
        #             row.set_focus_column(len(widget_list) - 2)
        #         if focus is not None:
        #             self._set_focus_position(focus_row + 1)

    def create_row(self, f, list_of_check_box_property_keys_and_nicknames, sorting):
        widget_list = []
        # Create the morea_id button
        button_label = u"\u25BA " + f.get_value_of_scalar_property("morea_id") + "\n"
        if f.get_value_of_scalar_property("title") != "":
            button_label += '   "' + bound_string(f.get_value_of_scalar_property("title"), 40) + '"'

        button = urwid.Button(button_label,
                              on_press=self.tui.handle_moreaid_button_press,
                              user_data=f)

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

        return row

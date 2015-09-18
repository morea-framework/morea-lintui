import time
import urwid
from Toolbox.toolbox import bound_string

__author__ = 'casanova'


class FocusRememberingButton(urwid.Button):
    def __init__(self, label, on_press=None, user_data=None, focus_memory=None):
        urwid.Button.__init__(self, label, on_press=on_press, user_data=user_data)
        self.focus_memory = focus_memory


class FocusRememberingCheckBox(urwid.CheckBox):
    def __init__(self, label, state=False, on_state_change=None, user_data=None, focus_memory=None):
        urwid.CheckBox.__init__(self, label, state=state, on_state_change=on_state_change, user_data=user_data)
        self.focus_memory = focus_memory


class TopLevelFrame(urwid.Pile):
    def __init__(self, _tui,
                 morea_type_key_and_nickname,
                 list_of_check_box_property_keys_and_nicknames,
                 sorting=False, focus_memory=None, sort_by_module_reference=False):

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
        # Create the header row
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

        # Create the display row
        file_to_row_index_mapping = {}
        for f in filelist:
            if sort_by_module_reference and f is None:
                row = urwid.Columns([urwid.AttrWrap(urwid.Text("\nUNREFERENCED BY ANY MODULE:"), 'dull')])
            elif sort_by_module_reference and f.get_value_of_scalar_property("morea_type") == "module":
                row = urwid.Columns([urwid.AttrWrap(urwid.Text("\nREFERENCE BY MODULE '" +
                                                               f.get_value_of_scalar_property("morea_id") + "':"),
                                                    'dull')])
            else:
                row = self.create_row(len(list_of_rows), f, list_of_check_box_property_keys_and_nicknames, sorting)
                file_to_row_index_mapping[f] = len(list_of_rows)

            list_of_rows.append(urwid.AttrWrap(row, 'topframe not selected', 'topframe selected'))

        # Create a blank row
        list_of_rows.append(urwid.Columns([FocusRememberingButton("", focus_memory=[f, len(list_of_rows), 0])], dividechars=1))

        # Create the pile
        urwid.Pile.__init__(self, list_of_rows)

        # Set the focus
        if focus_memory is not None:
            [f, focus_row_index, focus_column_index] = focus_memory
            if not sorting:
                # print "SETTING FOCUS to ",focus_row_index, focus_column_index
                # time.sleep(1)
                list_of_rows[focus_row_index].set_focus_column(focus_column_index)
                self.set_focus(focus_row_index)
            else:
                # TODO: Determine the focus row
                focus_row_index = file_to_row_index_mapping[f]
                list_of_rows[focus_row_index].set_focus_column(focus_column_index)
                self.set_focus(focus_row_index)

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

    def create_row(self, row_count, f, list_of_check_box_property_keys_and_nicknames, sorting):
        widget_list = []
        # Create the morea_id button
        button_label = u"\u25BA " + f.get_value_of_scalar_property("morea_id") + "\n"
        if f.get_value_of_scalar_property("title") != "":
            button_label += '   "' + bound_string(f.get_value_of_scalar_property("title"), 40) + '"'

        button = FocusRememberingButton(button_label,
                                        on_press=self.tui.handle_moreaid_button_press,
                                        user_data=f,
                                        focus_memory=[f, row_count, len(widget_list)])

        widget_list += [button]

        # Create list_of_checkboxes for required True/False fields
        list_of_centered_checkboxes = []
        for (k, n) in list_of_check_box_property_keys_and_nicknames:
            if f.get_value_of_scalar_property(k) is not None:
                cb = FocusRememberingCheckBox("",
                                              state=f.get_value_of_scalar_property(k),
                                              on_state_change=self.tui.handle_toplevelframe_checkbox_state_change,
                                              user_data=(f, k),
                                              focus_memory=[f, row_count,
                                                            len(widget_list) + len(list_of_centered_checkboxes)])
                list_of_centered_checkboxes.append(urwid.Padding(cb, align='center', width=len(n) - 2))
            else:
                list_of_centered_checkboxes.append(urwid.Text(""))

        widget_list += [(6, x) for x in list_of_centered_checkboxes]

        # Create the sorting buttons if needed
        if sorting:
            if f.get_value_of_scalar_property("morea_sort_order") is not None:
                button_up = FocusRememberingButton(u'\u25B2', on_press=self.tui.handle_module_sorting_button_press,
                                                   user_data=[-1, f],
                                                   focus_memory=[f, row_count,
                                                                 len(widget_list)])
                widget_list += [(2, button_up)]
                button_down = FocusRememberingButton(u'\u25bC', on_press=self.tui.handle_module_sorting_button_press,
                                                     user_data=[+1, f],
                                                     focus_memory=[f, row_count,
                                                                   len(widget_list)])
                widget_list += [(2, button_down)]
            else:
                button_up = urwid.Text(" ")
                widget_list += [(2, button_up)]
                button_down = urwid.Text(" ")
                widget_list += [(2, button_down)]

        row = urwid.Columns(widget_list, dividechars=1)

        return row

import urwid

from morealintui.MOREA.MoreaGrammar import MoreaGrammar
from morealintui.MOREA.MoreaProperty import Property, PropertyVersion
from morealintui.MOREA.MoreaPropertyVersion import ScalarPropertyValue
from morealintui.TUI.PopupDialog import HiddenPopupLauncher
from morealintui.Toolbox.toolbox import CustomException

__author__ = 'casanova'

max_label_width = max([len(x) for x in MoreaGrammar.property_syntaxes])

true_label = "[ True  ]"
false_label = "[ False ]"

commentedout_true_label = "#"
commentedout_false_label = " "


class ViewFrame(urwid.Pile):
    def __init__(self, tui, morea_file):
        self.tui = tui
        self.morea_file = morea_file
        self.popup_launcher = HiddenPopupLauncher(tui, self)

        # Compute the max width of field labels

        self.list_of_rows = []

        # Create the rows for all the file properties (only Yaml content)
        property_list = morea_file.property_list

        self.property_tui_dict = {}
        for pname in MoreaGrammar.property_output_order:
            if pname in property_list:
                # Build a class that embodies a property
                self.property_tui_dict[pname] = PropertyTui(self, morea_file, morea_file.property_list[pname])
                self.list_of_rows += self.property_tui_dict[pname].get_rows()
                self.list_of_rows.append(
                    urwid.Columns([urwid.Text("-----------------------------------------------------------")]))

        # Create an empty row
        self.list_of_rows.append(urwid.Columns([self.popup_launcher]))

        # Add all the rows in the pile
        urwid.Pile.__init__(self, self.list_of_rows)

    def save_content(self):

        # Build putative property starting with what we can get from the TUI
        putative_property_list = {}
        for pname in MoreaGrammar.property_syntaxes:
            if pname in self.property_tui_dict and len(self.property_tui_dict[pname].get_property().versions) != 0:
                putative_property_list[pname] = self.property_tui_dict[pname].get_property()
            elif pname in self.morea_file.property_list:
                putative_property_list[pname] = self.morea_file.property_list[pname]
            else:
                pass

        # print "PUTATIVE PROPERTYLIST:"
        # for pname in putative_property_list:
        #    putative_property_list[pname].display()
        # time.sleep(1000)

        # At this point we have the putative property and we try to apply changes
        # to the Morea content
        try:
            self.tui.content.apply_property_changes(self.morea_file, putative_property_list)
        except CustomException as e:
            raise e

        return


class PropertyTui:
    def __init__(self, viewframe, morea_file, prop):
        self.viewframe = viewframe
        self.morea_file = morea_file
        self.prop = prop
        self.version_tuis = []

        for v in self.prop.versions:
            self.version_tuis.append(PropertyVersionTui(self.viewframe, morea_file, prop, v))
        return

    def get_rows(self):
        row_list = []
        for vt in self.version_tuis:
            row_list = row_list + vt.get_rows()
        return row_list

    def get_property(self):
        p = Property(self.prop.name)
        for vt in self.version_tuis:
            version = vt.get_version()
            if version is not None:
                p.add_version(version)
        return p


class PropertyVersionTui:
    def __init__(self, viewframe, morea_file, prop, version):
        self.viewframe = viewframe
        self.morea_file = morea_file
        self.property = prop
        self.version = version

        # Single boolean value
        if not version.grammar.multiple_values and version.grammar.data_type == bool:
            self.instance = BoolanValueTui(morea_file, prop, version)
        elif prop.name == "morea_icon_url" or \
                        prop.name == "morea_url" or \
                        prop.name == "morea_icon_url":
            self.instance = NonEditableTextLine(morea_file, prop, version)
        elif prop.name == "title" or \
                        prop.name == "morea_summary" or \
                        prop.name == "morea_start_date" or \
                        prop.name == "morea_end_date":
            self.instance = EditableTextLine(morea_file, prop, version)
        elif prop.name == "morea_sort_order" or \
                        prop.name == "morea_id" or \
                        prop.name == "morea_type":
            self.instance = DisplayOnlyLine(morea_file, prop, version)
        elif prop.name == "morea_readings" or \
                        prop.name == "morea_outcomes" or \
                        prop.name == "morea_assessments" or \
                        prop.name == "morea_experiences" or \
                        prop.name == "morea_outcomes_assessed" or \
                        prop.name == "morea_prerequisites":
            self.instance = NonEditableMultiValues(viewframe, morea_file, prop, version)
        elif prop.name == "morea_labels":
            self.instance = EditableMultiValues(morea_file, prop, version)
        # Not implemented yet or ignored
        else:
            self.instance = TBDValueTui(morea_file, prop, version)
        return

    def get_rows(self):
        return self.instance.get_rows()

    def get_version(self):
        return self.instance.get_version()


class TBDValueTui:
    def __init__(self, morea_file, prop, version):
        self.row = urwid.Columns(
            [('fixed', 2, urwid.Text("  ")),
             ('fixed', max_label_width + 2, urwid.AttrWrap(urwid.Text(prop.name + ": "), 'duller')),
             urwid.AttrWrap(urwid.Text("[not viewable in TUI]"), 'duller')])

    def get_rows(self):
        return [self.row]

    # noinspection PyMethodMayBeStatic
    def get_version(self):
        return None


class NonEditableTextLine:
    def __init__(self, morea_file, prop, version):

        widget_list = []
        self.property = prop

        # Comment button
        if version.commented_out:
            self.comment_button = urwid.Button("#")
        else:
            self.comment_button = urwid.Button(" ")
        widget_list.append(('fixed', 2, urwid.AttrWrap(self.comment_button, 'commentout button')))
        urwid.connect_signal(self.comment_button, 'click', handle_simple_commentout_button_click,
                             [morea_file, prop, version])

        # Label
        widget_list.append(('fixed', max_label_width + 2, urwid.Text(prop.name + ": ")))

        # Text
        self.textfield = urwid.Text(version.get_scalar_value_even_if_commented_out())

        # self.textfield = urwid.Text("HELLO")
        widget_list.append(urwid.AttrWrap(self.textfield, 'dull'))

        self.row = urwid.Columns(widget_list)

    def get_rows(self):
        return [self.row]

    def get_version(self):

        commented_out = self.comment_button.get_label() == commentedout_true_label
        value = self.textfield.get_text()[0]

        # Create a value-less property version
        version = PropertyVersion(self.property.name, self.property.grammar, commented_out)
        # add a scalar value
        version.set_value(ScalarPropertyValue(commented_out, value))
        return version


class DisplayOnlyLine:
    def __init__(self, morea_file, prop, version):

        widget_list = []
        self.property = prop

        if version.commented_out:
            widget_list.append(('fixed', 2, urwid.AttrWrap(urwid.Text("#"), 'dull')))
        else:
            widget_list.append(('fixed', 2, urwid.Text(" ")))

        # Label
        widget_list.append(('fixed', max_label_width + 2, urwid.AttrWrap(urwid.Text(prop.name + ": "), 'dull')))

        # number
        self.textfield = urwid.Text(str(version.get_scalar_value_even_if_commented_out()))

        # self.textfield = urwid.Text("HELLO")
        widget_list.append(urwid.AttrWrap(self.textfield, 'dull'))

        self.row = urwid.Columns(widget_list)

    def get_rows(self):
        return [self.row]

    # noinspection PyMethodMayBeStatic
    def get_version(self):
        return None


class NonEditableMultiValues:
    def __init__(self, viewframe, morea_file, prop, version):

        self.viewframe = viewframe
        self.property = prop
        self.private_rows = []
        self.pile = None

        # Sanity check
        if not MoreaGrammar.property_syntaxes[prop.name].multiple_values:
            raise CustomException("  In NonEditableMultiValues: non multi value property!!")

        # ################## TOP ROW ####################

        widget_list = []

        # Comment button
        if version.commented_out:
            self.comment_button = urwid.Button("#")
        else:
            self.comment_button = urwid.Button(" ")
        widget_list.append(('fixed', 2, urwid.AttrWrap(self.comment_button, 'commentout button')))

        # Label
        widget_list.append(('fixed', max_label_width + 2, urwid.Text(prop.name + ": ")))

        toprow = urwid.Columns(widget_list)
        self.private_rows.append(toprow)

        list_of_text_widths = [len(str(v.value)) for v in version.values]
        if len(list_of_text_widths) > 0:
            max_text_width = max(list_of_text_widths) + 2
        else:
            max_text_width = 2

        # #################### OTHER ROWS #####################

        self.value_comment_buttons = []
        # At this point I know that version.values is a list
        for v in version.values:
            widget_list = []

            # blank offset
            widget_list.append(('fixed', 5, urwid.Text("     ")))

            # comment button
            commented_out = v.commented_out
            value = v.value
            if commented_out:
                comment_button = urwid.Button("#")
            else:
                comment_button = urwid.Button(" ")
            widget_list.append(('fixed', 2, urwid.AttrWrap(comment_button, 'commentout button')))
            self.value_comment_buttons.append(comment_button)

            urwid.connect_signal(comment_button, 'click', handle_multi_value_item_commentedout_button_click,
                                 self.comment_button)
            # dash
            widget_list.append(('fixed', 3, urwid.Text(" - ")))

            # field
            value_text = str(value)
            widget_list.append(('fixed', max_text_width, urwid.AttrWrap(urwid.Text(value_text), 'dull')))

            # up button
            up_button = urwid.Button(u'\u25B2', on_press=self.handle_up_down_button_click,
                                     user_data=[-1, value_text])
            widget_list.append(('fixed', 2, up_button))

            widget_list.append(('fixed', 1, urwid.Text('')))

            # down button
            down_button = urwid.Button(u'\u25bC', on_press=self.handle_up_down_button_click,
                                       user_data=[+1, value_text])
            widget_list.append(('fixed', 2, down_button))

            self.private_rows.append(urwid.Columns(widget_list))

        #########################
        # Signal for top button
        urwid.connect_signal(self.comment_button, 'click', handle_multi_value_top_commentedout_button_click,
                             self.value_comment_buttons)

        self.pile = urwid.Pile(self.private_rows)

    def handle_up_down_button_click(self, button, user_data):
        [direction, text_value] = user_data

        # Identify the row with that text value
        src_private_row_index = -1
        for index in xrange(1, len(self.private_rows)):
            if text_value == self.private_rows[index].contents[3][0].original_widget.get_text()[0]:
                src_private_row_index = index
                # print "FOUND IT!!"
                break

        if src_private_row_index == -1:
            raise CustomException("Internal error: couldn't find the private row!")

        # No-op
        if src_private_row_index == 1 and direction == -1:
            return
        if src_private_row_index == len(self.private_rows) - 1 and direction == 1:
            return

        dst_private_row_index = src_private_row_index + direction

        tmp = self.private_rows[dst_private_row_index]
        self.private_rows[dst_private_row_index] = self.private_rows[src_private_row_index]
        self.private_rows[src_private_row_index] = tmp

        newpile = urwid.Pile(self.private_rows)
        for index in xrange(0, len(self.viewframe.contents)):
            (widget, prop) = self.viewframe.contents[index]
            if widget is self.pile:
                # update the viewframe
                self.viewframe.contents[index] = (newpile, prop)
                # set the focus to this pile
                self.viewframe.set_focus(index)
                self.viewframe.contents[index][0].set_focus(dst_private_row_index)
                focus_column = 5 + direction
                self.viewframe.contents[index][0].contents[dst_private_row_index][0].set_focus_column(focus_column)
        self.pile = newpile
        self.viewframe.tui.main_loop.draw_screen()

        return

    def get_rows(self):
        return [self.pile]

    def get_version(self):

        commented_out = self.comment_button.get_label() == commentedout_true_label
        version = PropertyVersion(self.property.name, self.property.grammar, commented_out)

        values = []
        for index in xrange(1, len(self.private_rows)):
            button_label = self.private_rows[index].contents[1][0].original_widget.get_label()[0]
            commented_out = button_label == "#"
            value = self.private_rows[index].contents[3][0].original_widget.get_text()[0]
            values.append(ScalarPropertyValue(commented_out, value))

        version.set_value(values)
        return version


class EditableMultiValues:
    def __init__(self, morea_file, prop, version):

        widget_list = []
        self.property = prop
        self.rows = []

        # Sanity check
        if not MoreaGrammar.property_syntaxes[prop.name].multiple_values:
            raise CustomException("  In NonEditableMultiValues: non multi value property!!")

        # ################## TOP ROW ####################

        # Comment button
        if version.commented_out:
            self.comment_button = urwid.Button("#")
        else:
            self.comment_button = urwid.Button(" ")
        widget_list.append(('fixed', 2, urwid.AttrWrap(self.comment_button, 'commentout button')))

        # Label
        widget_list.append(('fixed', max_label_width + 2, urwid.Text(prop.name + ": ")))

        toprow = urwid.Columns(widget_list)
        self.rows.append(toprow)

        # #################### OTHER ROWS #####################

        self.contents = []
        # At this point I know that version.values is a list
        for v in version.values:
            widget_list = []

            # blank offset
            widget_list.append(('fixed', 5, urwid.Text("     ")))

            # comment button
            commented_out = v.commented_out
            value = v.value
            if commented_out:
                comment_button = urwid.Button("#")
            else:
                comment_button = urwid.Button(" ")
            widget_list.append(('fixed', 2, urwid.AttrWrap(comment_button, 'commentout button')))
            urwid.connect_signal(comment_button, 'click', handle_multi_value_item_commentedout_button_click,
                                 self.comment_button)
            # dash
            widget_list.append(('fixed', 3, urwid.Text(" - ")))

            # field
            edit_text = urwid.Edit(caption="", edit_text=str(value))
            widget_list.append(edit_text)

            self.contents.append((comment_button, edit_text))
            self.rows.append(urwid.Columns(widget_list))

        #########################
        # Signal for top button
        urwid.connect_signal(self.comment_button, 'click', handle_multi_value_top_commentedout_button_click,
                             [b for (b, c) in self.contents])

    def get_rows(self):
        return self.rows

    def get_version(self):

        commented_out = self.comment_button.get_label() == commentedout_true_label
        version = PropertyVersion(self.property.name, self.property.grammar, commented_out)

        values = []
        for (cbutton, edittext) in self.contents:
            commented_out = cbutton.get_label() == "#"
            value = edittext.get_edit_text()
            values.append(ScalarPropertyValue(commented_out, value))

        version.set_value(values)
        return version


class EditableTextLine:
    def __init__(self, morea_file, prop, version):

        widget_list = []
        self.property = prop

        # Comment button
        if version.commented_out:
            self.comment_button = urwid.Button("#")
        else:
            self.comment_button = urwid.Button(" ")
        widget_list.append(('fixed', 2, urwid.AttrWrap(self.comment_button, 'commentout button')))
        urwid.connect_signal(self.comment_button, 'click', handle_simple_commentout_button_click,
                             [morea_file, self.property, version])

        # Label
        widget_list.append(('fixed', max_label_width + 2, urwid.Text(self.property.name + ": ")))

        # Text
        self.textfield = urwid.Edit(caption="", edit_text=version.get_scalar_value_even_if_commented_out())
        # self.textfield = urwid.Text("HELLO")
        widget_list.append(self.textfield)

        self.row = urwid.Columns(widget_list)

    def get_rows(self):
        return [self.row]

    def get_version(self):
        commented_out = self.comment_button.get_label() == commentedout_true_label
        value = self.textfield.get_edit_text()

        # Create a value-less property version
        version = PropertyVersion(self.property.name, self.property.grammar, commented_out)
        # add a scalar value
        version.set_value(ScalarPropertyValue(commented_out, value))
        return version


class BoolanValueTui:
    def __init__(self, morea_file, prop, version):
        self.morea_file = morea_file
        self.property = prop
        self.version = version

        widget_list = []

        # Comment button
        if self.version.commented_out:
            self.comment_button = urwid.Button("#")
        else:
            self.comment_button = urwid.Button(" ")
        widget_list.append(('fixed', 2, urwid.AttrWrap(self.comment_button, 'commentout button')))
        urwid.connect_signal(self.comment_button, 'click', handle_simple_commentout_button_click,
                             [morea_file, prop, version])

        # Label
        widget_list.append(('fixed', max_label_width + 2, urwid.Text(prop.name + ": ")))

        # True/False button
        value = version.values.value

        if value:
            self.true_false_button = urwid.Button(true_label)
        else:
            self.true_false_button = urwid.Button(false_label)

        urwid.connect_signal(self.true_false_button, 'click', handle_true_false_button_click,
                             [morea_file, prop, version])
        self.true_false_button = urwid.AttrWrap(self.true_false_button, 'truefalse not selected', 'truefalse selected')

        widget_list.append(('fixed', 15, self.true_false_button))

        self.row = urwid.Columns(widget_list)

    def get_rows(self):
        return [self.row]

    def get_version(self):
        commented_out = self.comment_button.get_label() == commentedout_true_label
        value = self.true_false_button.get_label() == true_label

        # Create a value-less property version
        version = PropertyVersion(self.property.name, self.property.grammar, commented_out)
        # add a scalar value
        version.set_value(ScalarPropertyValue(commented_out, value))

        return version


def handle_true_false_button_click(button, user_data):
    if button.get_label() == true_label:
        button.set_label(false_label)
    else:
        button.set_label(true_label)
    return


def handle_simple_commentout_button_click(button, user_data):
    if button.get_label() == commentedout_true_label:
        button.set_label(commentedout_false_label)
    else:
        button.set_label(commentedout_true_label)
    return


def handle_multi_value_top_commentedout_button_click(button, user_data):
    value_comment_buttons = user_data
    if button.get_label() == commentedout_true_label:
        button.set_label(commentedout_false_label)
    else:
        button.set_label(commentedout_true_label)
        for b in value_comment_buttons:
            b.set_label(commentedout_true_label)
    return


def handle_multi_value_item_commentedout_button_click(button, user_data):
    top_button = user_data
    if button.get_label() == commentedout_true_label:
        button.set_label(commentedout_false_label)
        top_button.set_label(commentedout_false_label)
    else:
        button.set_label(commentedout_true_label)

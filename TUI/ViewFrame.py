import time

import urwid

from MOREA.MoreaGrammar import MoreaGrammar
from MOREA.MoreaProperty import Property, PropertyVersion
from MOREA.MoreaPropertyVersion import ScalarPropertyValue
from Toolbox.toolbox import CustomException

__author__ = 'casanova'

max_label_width = max([len(x) for x in MoreaGrammar.property_syntaxes])

true_label = "[ True  ]"
false_label = "[ False ]"

commentedout_true_label = "#"
commentedout_false_label = " "


class PopUpDialog(urwid.WidgetWrap):
    """A dialog that appears with nothing but a close button """
    signals = ['close']

    def __init__(self, msg):
        close_button = urwid.Button("OK")
        urwid.connect_signal(close_button, 'click',
                             lambda button: self._emit("close"))
        pile = urwid.Pile([urwid.Text("Can't save due to the following:\n" + msg),
                           urwid.Columns([(10, urwid.Text(" ")), (
                               10, urwid.AttrWrap(close_button, 'truefalse not selected', 'truefalse selected'))])])
        fill = urwid.Filler(pile)
        super(PopUpDialog, self).__init__(urwid.AttrWrap(fill, 'popbg'))


class SaveButtonWithAPopup(urwid.PopUpLauncher):
    def __init__(self, tui, viewframe, morea_file):
        self.tui = tui
        self.viewframe = viewframe
        self.morea_file = morea_file
        self.popup_message = ""
        super(SaveButtonWithAPopup, self).__init__(urwid.Button("CONFIRM"))
        # urwid.connect_signal(self.original_widget, 'click',
        #                      self.open_the_pop_up, None)
        urwid.connect_signal(self.original_widget, 'click',
                             # self.viewframe.handle_viewframe_save(), None)
                             self.open_the_pop_up)

    def create_pop_up(self):
        pop_up = PopUpDialog(self.popup_message)
        urwid.connect_signal(pop_up, 'close',
                             lambda button: self.close_pop_up())
        return pop_up

    def open_the_pop_up(self, button):

        try:
            self.viewframe.handle_viewframe_save()
        except CustomException as e:
            self.popup_message = str(e)
            self.open_pop_up()
            return

        # Close the mainviewer frame
        self.tui.frame_holder.set_body(
            self.tui.top_level_frame_dict[self.morea_file.get_value_of_scalar_property("morea_type")])
        self.tui.main_loop.draw_screen()

    def get_pop_up_parameters(self):
        return {'left': -4, 'top': -10, 'overlay_width': 70, 'overlay_height': 15}


class ViewFrame(urwid.Pile):
    def __init__(self, _tui, morea_file):
        self.tui = _tui
        self.morea_file = morea_file

        # Compute the max width of field labels

        self.list_of_rows = []

        # Create the rows for all the file properties (only Yaml content)
        property_list = morea_file.property_list

        self.property_tui_dict = {}
        for pname in MoreaGrammar.property_output_order:
            if pname in property_list:
                # Build a class that embodies a property
                self.property_tui_dict[pname] = PropertyTui(morea_file, morea_file.property_list[pname])
                self.list_of_rows += self.property_tui_dict[pname].get_rows()
                self.list_of_rows.append(
                    urwid.Columns([urwid.Text("-----------------------------------------------------------")]))

        # Create an empty row
        self.list_of_rows.append(urwid.Columns([]))

        # Create the last row

        self.cancel_button = urwid.Button("CANCEL", on_press=self.handle_viewframe_cancel, user_data=None)
        self.save_button = SaveButtonWithAPopup(self.tui, self, self.morea_file)

        last_row = urwid.Columns(
            [(11, urwid.AttrWrap(self.cancel_button, 'truefalse not selected', 'truefalse selected')),
             (11, urwid.AttrWrap(self.save_button, 'truefalse not selected', 'truefalse selected'))],
            dividechars=1)

        self.list_of_rows.append(last_row)

        # Add all the rows in the pile
        urwid.Pile.__init__(self, self.list_of_rows)

    def handle_viewframe_cancel(self, button):
        # Simply show the correct toplevel_frame
        self.tui.frame_holder.set_body(
            self.tui.top_level_frame_dict[self.morea_file.get_value_of_scalar_property("morea_type")])
        self.tui.main_loop.draw_screen()
        return

    def handle_viewframe_save(self):

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

        # At this point we have the putative property
        try:
            self.tui.content.apply_property_changes(self.morea_file, putative_property_list)
        except CustomException as e:
            raise e
        return


class PropertyTui:
    def __init__(self, morea_file, prop):
        self.morea_file = morea_file
        self.prop = prop
        self.version_tuis = []

        for v in self.prop.versions:
            self.version_tuis.append(PropertyVersionTui(morea_file, prop, v))
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
    def __init__(self, morea_file, prop, version):
        self.morea_file = morea_file
        self.property = prop
        self.version = version

        # Single boolean value
        if not version.grammar.multiple_values and version.grammar.data_type == bool:
            self.instance = BoolanValueTui(morea_file, prop, version)
        elif prop.name == "morea_icon_url" or \
                        prop.name == "morea_url":
            self.instance = NonEditableTextLine(morea_file, prop, version)
        elif prop.name == "title" or \
                prop.name == "morea_summary":
            self.instance = EditableTextLine(morea_file, prop, version)
        elif prop.name == "morea_sort_order" or \
                prop.name == "morea_id" or \
                prop.name == "morea_type":
            self.instance = DisplayOnlyLine(morea_file, prop, version)
        elif prop.name == "morea_readings" or \
                prop.name == "morea_outcomes" or \
                prop.name == "morea_assessments" or \
                prop.name == "morea_experiences" or \
                prop.name == "morea_labels" or \
                prop.name == "morea_outcomes_assessed":
            self.instance = NonEditableMultiValues(morea_file, prop, version)
        # Not implemented yet / ignores
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

    def get_version(self):
        return None


class NonEditableMultiValues:
    def __init__(self, morea_file, prop, version):

        widget_list = []
        self.property = prop
        self.rows = []

        # Sanity check
        if not MoreaGrammar.property_syntaxes[prop.name].multiple_values:
            raise CustomException("  In NonEditableMultiValues: non multi value property!!")

        ################### TOP ROW ####################

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

        ##################### OTHER ROWS #####################

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
            value_text = str(value)
            widget_list.append(urwid.Text(value_text))

            self.contents.append((comment_button, value_text))
            self.rows.append(urwid.Columns(widget_list))

        #########################
        # Signal for top button
        urwid.connect_signal(self.comment_button, 'click', handle_multi_value_top_commentedout_button_click,
                             self.contents)

    def get_rows(self):
        return self.rows

    def get_version(self):

        commented_out = self.comment_button.get_label() == commentedout_true_label
        version = PropertyVersion(self.property.name, self.property.grammar, commented_out)

        values = []
        for (cbutton, vtext) in self.contents:
            commented_out = cbutton.get_label() == "#"
            value = vtext
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
    contents = user_data
    if button.get_label() == commentedout_true_label:
        # print "LABLE IS TRUE< SETTING TO FALSE"
        # time.sleep(10)
        button.set_label(commentedout_false_label)
    else:
        # print "LABLE IS FALSE< SETTING TO TRUE"
        # time.sleep(10)

        button.set_label(commentedout_true_label)
        for (b, t) in contents:
            b.set_label(commentedout_true_label)
    return


def handle_multi_value_item_commentedout_button_click(button, user_data):
    top_button = user_data
    if button.get_label() == commentedout_true_label:
        button.set_label(commentedout_false_label)
        top_button.set_label(commentedout_false_label)
    else:
        button.set_label(commentedout_true_label)

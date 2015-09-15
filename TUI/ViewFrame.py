import time

import urwid

import MOREA
from MOREA.MoreaGrammar import MoreaGrammar
from MOREA.MoreaProperty import Property, ScalarPropertyValue, PropertyVersion

__author__ = 'casanova'

max_label_width = max([len(x) for x in MoreaGrammar.property_syntaxes])

true_label = "[ True  ]"
false_label = "[ False ]"

commentedout_true_label = "#"
commentedout_false_label = " "


class ViewFrame(urwid.Pile):
    def __init__(self, _tui, morea_file):
        self.tui = _tui
        self.morea_file = morea_file

        # Compute the max width of field labels

        self.list_of_rows = []

        # Create the rows for all the file properties (only Yaml content)
        property_list = morea_file.property_list

        self.property_tui_dict = {}
        for pname in property_list:
            # Build a class that embodies a property
            self.property_tui_dict[pname] = PropertyTui(morea_file, morea_file.property_list[pname])
            self.list_of_rows += self.property_tui_dict[pname].get_rows()

        # Create an empty row
        self.list_of_rows.append(urwid.Columns([]))

        # Create the last row
        cancel_button = urwid.Button("Cancel", on_press=self.handle_viewframe_cancel, user_data=[None])
        save_button = urwid.Button("Save", on_press=self.handle_viewframe_save, user_data=[None])
        last_row = urwid.Columns([(10, urwid.AttrWrap(cancel_button, 'truefalse not selected', 'truefalse selected')),
                                  (10, urwid.AttrWrap(save_button, 'truefalse not selected', 'truefalse selected'))],
                                 dividechars=1)
        self.list_of_rows.append(last_row)

        # Add all the rows in the pile
        urwid.Pile.__init__(self, self.list_of_rows)

    def handle_viewframe_cancel(self, button, user_data):
        # Simply show the correct toplevel_frame
        self.tui.frame_holder.set_body(
            self.tui.top_level_frame_dict[self.morea_file.get_value_of_scalar_property("morea_type")])
        self.tui.main_loop.draw_screen()
        return

    def handle_viewframe_save(self, button, user_data):
        putative_property_list = {}
        for pname in self.property_tui_dict:
            putative_property_list[pname] = self.property_tui_dict[pname].get_property()

        # print "PROPERTYLIST:"
        # for pname in putative_property_list:
        #    putative_property_list[pname].display()
        # time.sleep(1000)

        # At this point we have the putative property
        # Go through the properties, and replace the
        # TODO
        print "SHOULD DO SOMETIHNG!!!"
        time.sleep(2)


        # Close this frame
        self.tui.frame_holder.set_body(
            self.tui.top_level_frame_dict[self.morea_file.get_value_of_scalar_property("morea_type")])
        self.tui.main_loop.draw_screen()


class PropertyTui:
    def __init__(self, morea_file, property):
        self.morea_file = morea_file
        self.property = property
        self.version_tuis = []

        for v in self.property.versions:
            self.version_tuis.append(PropertyVersionTui(morea_file, property, v))
        return

    def get_rows(self):
        row_list = []
        for vt in self.version_tuis:
            row_list = row_list + vt.get_rows()
        return row_list

    def get_property(self):
        p = Property(self.property.name)
        for vt in self.version_tuis:
            version = vt.get_version()
            if version is not None:
                p.add_property_version(version)
        return p


class PropertyVersionTui:
    def __init__(self, morea_file, property, version):
        self.morea_file = morea_file
        self.property = property
        self.version = version

        if not version.grammar.multiple_values and version.grammar.data_type == bool:
            self.instance = BoolanValueTui(morea_file, property, version)
        else:
            self.instance = TBDValueTui(morea_file, property, version)
        return

    def get_rows(self):
        return self.instance.get_rows()

    def get_version(self):
        return self.instance.get_version()


class TBDValueTui:
    def __init__(self, morea_file, property, version):
        self.row = urwid.Columns(
            [('fixed', 2, urwid.Text("  ")), ('fixed', max_label_width + 2, urwid.Text(property.name + ": ")),
             urwid.Text("       n/a")])

    def get_rows(self):
        return [self.row]

    def get_version(self):
        return None


class BoolanValueTui:
    def __init__(self, morea_file, property, version):
        self.morea_file = morea_file
        self.property = property
        self.version = version

        widget_list = []

        # Comment button
        if self.version.commented_out:
            self.comment_button = urwid.Button("#")
        else:
            self.comment_button = urwid.Button(" ")
        widget_list.append(('fixed', 2, self.comment_button))
        urwid.connect_signal(self.comment_button, 'click', handle_commentedout_button_click,
                             [morea_file, property, version])

        # Label
        widget_list.append(('fixed', max_label_width + 2, urwid.Text(property.name + ": ")))

        # True/False button
        value = version.values.value
        if value:
            self.true_false_button = urwid.Button(true_label)
        else:
            self.true_false_button = urwid.Button(false_label)

        urwid.connect_signal(self.true_false_button, 'click', handle_true_false_button_click,
                             [morea_file, property, version])
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
        version.add_scalar_property_value(ScalarPropertyValue(commented_out, value))

        return version


def handle_true_false_button_click(button, user_data):
    if button.get_label() == true_label:
        button.set_label(false_label)
    else:
        button.set_label(true_label)
    return


# TODO MAKE IT SO THAT COMMENTING HAPPENS CORRECTLY
def handle_commentedout_button_click(button, user_data):
    if button.get_label() == commentedout_true_label:
        button.set_label(commentedout_false_label)
    else:
        button.set_label(commentedout_true_label)
    return

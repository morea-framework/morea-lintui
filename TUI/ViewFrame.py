import time
import urwid
import MOREA

__author__ = 'casanova'

max_label_width = max([len(x) for x in MOREA.MoreaGrammar.MoreaGrammar.property_syntaxes])

true_label = "[ True  ]"
false_label = "[ False ]"

commentedout_true_label = "#"
commentedout_false_label = " "


class ViewFrame(urwid.Pile):
    def __init__(self, _tui, morea_file):
        self.tui = _tui

        # Compute the max width of field labels

        self.list_of_rows = []

        # Create the rows for all the file properties (only Yaml content)
        property_list = morea_file.property_list

        for pname in property_list:
            # Build a class that embodies a property
            property_tui = PropertyTui(morea_file, morea_file.property_list[pname])
            self.list_of_rows += property_tui.get_rows()

        # Create an empty row
        self.list_of_rows.append(urwid.Columns([]))

        # Create the last row
        cancel_button = urwid.Button("Cancel", on_press=self.tui.handle_viewframe_cancel, user_data=morea_file)
        save_button = urwid.Button("Save")
        last_row = urwid.Columns([(10, urwid.AttrWrap(cancel_button, 'truefalse not selected', 'truefalse selected')),
                                  (10, urwid.AttrWrap(save_button, 'truefalse not selected', 'truefalse selected'))],
                                 dividechars=1)
        self.list_of_rows.append(last_row)

        # Add all the rows in the pile
        urwid.Pile.__init__(self, self.list_of_rows)


class PropertyTui:
    def __init__(self, morea_file, property):
        self.morea_file = morea_file
        self.property = property
        self.versions = []

        for v in self.property.versions:
            self.versions.append(PropertyVersionTui(morea_file, property, v))

        return

    def get_rows(self):
        row_list = []
        for v in self.versions:
            row_list = row_list + v.get_rows()
        return row_list


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

    def apply_changes(self):
        # TODO
        return


class TBDValueTui:
    def __init__(self, morea_file, property, version):
        self.row = urwid.Columns(
            [('fixed', 2, urwid.Text("  ")), ('fixed', max_label_width + 2, urwid.Text(property.name + ": ")),
             urwid.Text("       n/a")])

    def get_rows(self):
        return [self.row]


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



def handle_true_false_button_click(button, user_data):
    if button.get_label() == true_label:
        button.set_label(false_label)
    else:
        button.set_label(true_label)
    return


# TODO MAKE IT SO THAT COMMENTING HAPPENS CORECTLY
def handle_commentedout_button_click(button, user_data):
    if button.get_label() == commentedout_true_label:
        button.set_label(commentedout_false_label)
    else:
        button.set_label(commentedout_true_label)
    return

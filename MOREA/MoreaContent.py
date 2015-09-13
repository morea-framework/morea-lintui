import os
import re

from Toolbox import toolbox
from Toolbox.toolbox import CustomException
from MoreaFile import MoreaFile
from MoreaGrammar import MoreaGrammar

__author__ = 'casanova'


class MoreaContent(object):
    """ A class for the whole MOREA Web site content """

    def __init__(self):
        self.files = []

    def acquire_all_content(self, root, parse_comments):
        if not os.path.isdir(root):
            raise CustomException("Can't find master/src/morea in the working directory... aborting!")

        err = False
        err_msg = ""
        self.files = []
        for path, subs, files in os.walk(root):
            for f in files:
                if re.match(".*.md$", f) is not None:
                    try:
                        f = MoreaFile(path + "/" + f, warnings=True, parse_comments=parse_comments)
                        self.files.append(f)
                    except CustomException as e:
                        err_msg += str(e)
                        err = True
        if err:
            raise CustomException(err_msg)

        print "  Acquired content from " + str(len(self.files)) + " MOREA .md files"
        return

    def take_pickles(self):
        for f in self.files:
            toolbox.morea_file_monitor.has_changed(f)
        return

    def check(self):
        try:
            self.type_check()
            self.reference_check()
            self.check_for_sort_order_collisions("module")
            self.check_for_sort_order_collisions("outcome")
        except CustomException as e:
            raise e
        return

    def type_check(self):

        print "  Type-checking..."

        err_msg = ""
        for f in self.files:
            # print "****************************", f.path
            try:
                f.typecheck()
            except CustomException as e:
                err_msg += f.path + ":\n" + unicode(e)

        if err_msg != "":
            raise CustomException(err_msg)

        return

    def reference_check(self):

        try:
            print "  Checking for duplicate ids..."
            self.check_for_duplicate_ids()

            print "  Checking for dangling references..."
            self.check_for_invalid_references()

        except CustomException as e:
            raise e

        return

    def check_for_duplicate_ids(self):
        err_msg = ""

        # Build list of ALL ids
        morea_ids = [[f.path, f.get_value_of_scalar_property("morea_id")] for f in self.files]

        # Find duplicates (very inefficient, but makes error reporting nice)
        for [path, morea_id] in morea_ids:
            if len([[p, i] for [p, i] in morea_ids if morea_id == i]) > 1:
                err_msg += "  Error: Duplicated morea_id " + morea_id + " (one occurrence in file " + path + ")\n"

        if err_msg != "":
            raise CustomException(err_msg)

        return

    def check_for_invalid_references(self):

        err_msg = ""

        for f in self.files:
            reference_list = f.get_reference_list()
            for [label, idstring] in reference_list:
                if idstring is not None:
                    try:
                        referenced_file = self.get_file(idstring)
                    except CustomException:
                        err_msg += "  Error: " + f.path + " references unknown morea_id " + idstring + "\n"
                        continue

                    morea_type = referenced_file.get_value_of_scalar_property("morea_type")
                    if not MoreaGrammar.is_valid_reference(label, morea_type):
                        print "label=", label, "idstring= ", idstring
                        err_msg += "  Error: File " + f.path + " mistakenly references id " + idstring + \
                                   ", which is of type " + \
                                   referenced_file.get_value_of_scalar_property("morea_type") + \
                                   ", as part of " + label + "\n"

        if err_msg != "":
            raise CustomException(err_msg)

        return

    def check_for_sort_order_collisions(self, filetype):
        err_msg = ""

        # Doing is for modules
        module_files = [f for f in self.files if f.get_value_of_scalar_property("morea_type") == filetype]

        # Sort files by sort order
        module_files.sort(key=lambda x: x.get_value_of_scalar_property("morea_sort_order"), reverse=False)
        for i in xrange(1, len(module_files)):
            current = module_files[i].get_value_of_scalar_property("morea_sort_order")
            previous = module_files[i - 2].get_value_of_scalar_property("morea_sort_order")
            if previous is not None and current == previous:
                err_msg += "  Error: Files " + module_files[i].path + " and " + \
                           module_files[i - 1].path + " have identical morea_sort_order values (" + str(current) + ")\n"

        if err_msg != "":
            raise CustomException(err_msg)

        return

    def get_file(self, id_string):
        for f in self.files:
            if f.get_value_of_scalar_property("morea_id") == id_string:
                return f
        raise CustomException("")

    def get_filelist_for_type(self, type_string):
        filelist = []
        for f in self.files:
            if f.get_value_of_scalar_property("morea_type") == type_string:
                filelist.append(f)
        return filelist

    def update_file_sort_order(self, morea_file, direction):

        if morea_file.get_value_of_scalar_property("morea_sort_order") is None:
            return

        # This is a TOTAL HACK!!!!

        # Build a sorted list
        sorted_list = sorted(self.get_filelist_for_type(morea_file.get_value_of_scalar_property("morea_type")),
                             key=lambda x: x.get_value_of_scalar_property("morea_sort_order"),
                             reverse=False)

        # Decide whether there is anything to do
        if direction == -1:
            index = sorted_list.index(file)
            if (index == 0) or (sorted_list[index - 1].get_value_of_scalar_property("morea_sort_order") is None):
                return
        else:  # direction = +1
            index = sorted_list.index(file)
            if (index == len(sorted_list) - 1) or \
                    (sorted_list[index + 1].get_value_of_scalar_property("morea_sort_order") is None):
                return

        # Multiply all the sort_orders by 2, to create space
        for f in self.files:
            sort_order = f.get_value_of_scalar_property("morea_sort_order")
            if sort_order is not None:
                f.set_value_of_scalar_property("morea_sort_order", 2 * sort_order)

        # Udpate
        index = sorted_list.index(morea_file)

        if direction == -1:
            morea_file.set_value_of_scalar_property("morea_sort_order",
                                                    sorted_list[index - 1].get_value_of_scalar_property(
                                                        "morea_sort_order") - 1)
        else:
            morea_file.set_value_of_scalar_property("morea_sort_order",
                                                    sorted_list[index + 1].get_value_of_scalar_property(
                                                        "morea_sort_order") + 1)

        # Re-sort the list it all
        sorted_list.sort(key=lambda x: x.get_value_of_scalar_property("morea_sort_order"),
                         reverse=False)

        # RE-compact it all using 10-increments
        counter = 10
        for f in sorted_list:
            if f.get_value_of_scalar_property("morea_sort_order") is not None:
                f.set_value_of_scalar_property("morea_sort_order", counter)
                counter += 10

        return

    def save(self):
        for f in self.files:
            f.save()
        return

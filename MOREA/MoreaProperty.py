from MOREA import MoreaGrammar
from MOREA.MoreaPropertyVersion import PropertyVersion
from Toolbox.toolbox import CustomException, add_quotes
from YamlParsingTools import decommentify

__author__ = 'casanova'


class Property(object):
    """A class that describes a morea property"""

    def __init__(self, name):
        self.name = name
        self.versions = []
        self.grammar = MoreaGrammar.MoreaGrammar.property_syntaxes[self.name]
        return

    # Creating the version from content (i.e., values) that can
    # be commented out
    def create_and_add_version(self, commented_out, value):
        # print "IN ADD_VERSION: ", self.name, commented_out, value
        try:
            version = PropertyVersion(self.name, self.grammar, commented_out)
            version.create_value_from_commentified_md_data(value)
        except CustomException as e:
            raise e

        self.versions.append(version)

    # To be called by the TUI, most likely
    def add_version(self, version):
        self.versions.append(version)

    def has_uncommented_versions(self):
        for version in self.versions:
            if not version.commented_out:
                return True
        return False

    def get_first_uncommented_scalar_value(self):
        for version in self.versions:
            value = version.get_first_uncommented_scalar_value()
            if value is not None:
                return value

    def comment_out_all_references_to_id(self, morea_id):
        for version in self.versions:
            version.comment_out_all_references_to_id(morea_id)
        return

    def display(self):
        # print "Property " + self.name + ":"
        for version in self.versions:
            version.display()

    def num_uncommented_versions(self):
        return len([v for v in self.versions if not v.commented_out])

    # Useful for the test suite
    def flatten(self):
        flattened = []
        for version in self.versions:
            flattened.append(version.flatten())
        return flattened

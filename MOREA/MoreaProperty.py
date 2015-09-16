from MOREA import MoreaGrammar
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

    # To be called when parsing
    def add_version(self, commented_out, value):
        # print "IN ADD_VERSION: ", self.name, commented_out, value
        try:
            version = PropertyVersion(self.name, self.grammar, commented_out)
            version.add_value(value)
        except CustomException as e:
            raise e

        self.versions.append(version)

    # To be called by the TUI, most likely
    def add_property_version(self, version):
        self.versions.append(version)

    def has_uncommented_versions(self):
        for version in self.versions:
            if not version.commented_out:
                return True
        return False

    def get_scalar_value(self):

        for version in self.versions:
            value = version.get_scalar_value()
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


    # Useful for testing
    def flatten(self):
        flattened = []
        for version in self.versions:
            flattened.append(version.flatten())
        return flattened


class PropertyVersion(object):
    """A class that describes a version of a morea property
        Values are PropertyScalarValue
        If the property is an atom, then it's a single value thing ("a: b")
        otherwise it's a list  thing ("a:\n -d\n -r\n")"""

    def __init__(self, name, grammar, commented_out):
        self.name = name
        self.grammar = grammar
        self.commented_out = commented_out
        self.values = []

        return

    # To be called when parsing
    def add_value(self, value):
        # print "IN PROPERTY VERSION add_value:", name, commented_out, value

        if type(value) != list:
            self.values = ScalarPropertyValue(self.commented_out, value)  #
        else:
            self.values = []
            for val in value:
                if val is not None:
                    # print "IN PROPERTYVERSION DECOMMENTIFYING: ", val
                    (decommentified_value, value_commented_out) = decommentify(val)
                    # print "    ---> ", decommentified_value, value_commented_out
                    if self.commented_out is True and value_commented_out is False:
                        raise CustomException("  Fishy commenting for (commented out) " +
                                              self.name + " field" + "\n" + "\n")
                    self.values.append(ScalarPropertyValue(value_commented_out, decommentified_value))

        return

    # Neded by the TUI
    def add_scalar_property_value(self, property_scalar_value):
        self.values = property_scalar_value
#        self.values.append(property_scalar_value)

    def get_scalar_value(self):
        if not self.commented_out:
            if type(self.values) != list:
                if not self.values.commented_out:
                    return self.values.value
            else:
                for val in self.values:
                    if not val.commented_out:
                        return val.value
        return None

    def get_scalar_value_even_if_commented_out(self):
        if type(self.values) != list:
                return self.values.value
        else:
            for val in self.values:
                    return val.value


    def comment_out_all_references_to_id(self, morea_id):
        for scalarvalue in self.values:
            if scalarvalue.value == morea_id:
                scalarvalue.commented_out = True
        return

    def display(self):
        print self.name + "(" + "commented_out: " + str(self.commented_out) + ")"
        if type(self.values) != list:
            print "\t(" + str(self.values.commented_out) + ", " + str(self.values.value) + ")"
        else:
            for val in self.values:
                print "\t-  (" + str(val.commented_out) + ", " + str(val.value) + ")"
        return

    def to_string(self):
        string = ""
        if self.commented_out:
            string += "#" + self.name + ": "
        else:
            string += "" + self.name + ": "

        if self.values is None or self.values is []:
            string += "\n"
            return string

        if not self.grammar.multiple_values:
            # Then it's a single value
            if type(self.values) == list:
                value = self.values[0].value
            else:
                # noinspection PyUnresolvedReferences
                value = self.values.value
            string += add_quotes(self.grammar.quoted, str(value)) + "\n"
            return string

        string += "\n"
        if type(self.values) != list:
            value_list = [self.values]
        else:
            value_list = self.values
        for v in value_list:
            if v.value is None:
                string += "\n"
                continue
            if self.commented_out or v.commented_out:
                string += "#  - " + add_quotes(self.grammar.quoted, str(v.value)) + "\n"
            else:
                string += "  - " + add_quotes(self.grammar.quoted, str(v.value)) + "\n"
        return string

    def num_of_uncommented_values(self):
        if type(self.values) != list:
            return self.commented_out
        else:
            return len([x for x in self.values if x.commented_out is False])

    def flatten(self):

        if type(self.values) != list:
            # noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
            flattened_value = (self.values.commented_out, self.values.value)
        else:
            flattened_value = []
            for val in self.values:
                flattened_value.append((val.commented_out, val.value))
        return [self.commented_out, flattened_value]


class ScalarPropertyValue(object):
    """ A simple class for better software engineering """

    def __init__(self, commented_out, value):
        self.commented_out = commented_out
        self.value = value

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

    def add_version(self, commented_out, value):
        # print "IN ADD_VERSION: ", self.name, commented_out, value
        try:
            version = PropertyVersion(self.name, self.grammar, commented_out, value)
        except CustomException as e:
            raise e

        self.versions.append(version)

    def has_uncommented_versions(self):
        for version in self.versions:
            if not version.commented_out:
                return True
        return False

    def display(self):
        # print "Property " + self.name + ":"
        for version in self.versions:
            version.display()

    # Useful for testing
    def flatten(self):
        flattened = []
        for version in self.versions:
            flattened.append(version.flatten())
        return flattened


class PropertyVersion(object):
    """A class that descibes a version of a morea property
        Values are PropertyScalarValue
        If the property is an atom, then it's a single value thing ("a: b")
        otherwise it's a list  thing ("a:\n -d\n -r\n")"""

    def __init__(self, name, grammar, commented_out, value):
        self.name = name
        self.grammar = grammar
        self.commented_out = commented_out
        self.values = []

        # print "IN PROPERTY VERSION CONS:", name, commented_out, value


        if type(value) != list:
            self.values = PropertyScalarValue(commented_out, value)  #
        else:
            self.values = []
            for val in value:
                if val is not None:
                    # print "IN PROPERTYVERSION ECOMMENTIFYING: ", val
                    (decommentified_value, value_commented_out) = decommentify(val)
                    # print "    ---> ", decommentified_value, value_commented_out
                    if self.commented_out is True and value_commented_out is False:
                        raise CustomException("  Fishy commenting for (commented out) " +
                                              name + " field" + "\n" + "\n")
                    self.values.append(PropertyScalarValue(value_commented_out, decommentified_value))

        return

    def display(self):
        print self.name + "(" + "commented_out: " + str(self.commented_out) + ")"
        print "\t" + str(self.values)

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
                string +=  "\n"
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
            flattened_value = (self.values.commented_out, self.values.value)
        else:
            flattened_value = []
            for val in self.values:
                flattened_value.append((val.commented_out, val.value))
        return [self.commented_out, flattened_value]


class PropertyScalarValue(object):
    """ A simple class for better software engineering """

    def __init__(self, commented_out, value):
        self.commented_out = commented_out
        self.value = value

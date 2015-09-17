from MOREA import MoreaGrammar
from Toolbox.toolbox import CustomException, add_quotes
from YamlParsingTools import decommentify

__author__ = 'casanova'


class ScalarPropertyValue(object):
    """ A simple class for better software engineering """

    def __init__(self, commented_out, value):
        self.commented_out = commented_out
        self.value = value


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

    def create_value_from_commentified_md_data(self, value):
        #print "IN PROPERTY VERSION add_value:", self.name, self.commented_out, value

        # Deal with single values
        if not self.grammar.multiple_values:
            if type(value) == list:
                if len(value) > 1:
                   raise CustomException("  Expecting single value for property '"+self.name+"' but got multiple")
                else:
                    self.values = ScalarPropertyValue(self.commented_out, value[0])
            else:
                self.values = ScalarPropertyValue(self.commented_out, value)
            return

        if type(value) != list:
            value = [value]

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

    def set_value(self, value):
        self.values = value

    def get_first_uncommented_scalar_value(self):
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

    def num_of_uncommented_values(self):
        if type(self.values) != list:
            return self.commented_out
        else:
            return len([x for x in self.values if x.commented_out is False])

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

    def flatten(self):

        if type(self.values) != list:
            # noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
            flattened_value = (self.values.commented_out, self.values.value)
        else:
            flattened_value = []
            for val in self.values:
                flattened_value.append((val.commented_out, val.value))
        return [self.commented_out, flattened_value]

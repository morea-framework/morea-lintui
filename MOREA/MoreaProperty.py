from Toolbox.toolbox import CustomException
from YamlParsingTools import decommentify

__author__ = 'casanova'


class Property(object):
    """A class that describes a morea property"""

    def __init__(self, name):
        self.name = name
        self.versions = []

        return

    def add_version(self, commentedout, value):
        # print "IN ADD_VERSION: ", self.name, commentedout, value
        try:
            version = PropertyVersion(self.name, commentedout, value)
        except CustomException as e:
            raise e

        self.versions.append(version)

    def has_uncommented_versions(self):
        for version in self.versions:
            if not version.commentedout:
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
        Values are tuples
        If the property is a tuple, then it's a single value thing ("a: b")
        otherwise it's a multuple value thing ("a:\n -d\n -r\n")"""

    def __init__(self, name, commentedout, value):
        self.name = name
        self.commentedout = commentedout
        self.values = []

        # print "IN PROPERTY VERSION CONS:", name, commentedout, value

        if type(value) != list:
            self.values = (commentedout, value)  # Tag the single value with the commented
            # out status of the version
        else:
            self.values = []
            for val in value:
                if val is not None:
                    #print "IN PROPERTYVERSION ECOMMENTIFYING: ", val
                    (decommentified_value, value_commentedout) = decommentify(val)
                    # print "    ---> ", decommentified_value, value_commentedout
                    if self.commentedout is True and value_commentedout is False:
                        raise CustomException("  Fishy commenting for (commented out) " +
                                              name + " field" + "\n" + "\n")
                    self.values.append((value_commentedout, decommentified_value))

        return

    def display(self):
        print self.name + "(" + "commentedout: "+str(self.commentedout) + ")"
        print "\t"+str(self.values)

    def num_of_uncommented_values(self):
        if type(self.values) != list:
            return self.values[0]
        else:
            return len([x for x in self.values if x[0] is False])

    def flatten(self):
        return [self.commentedout, self.values]

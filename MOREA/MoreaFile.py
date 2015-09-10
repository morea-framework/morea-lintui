from YamlParsingTools import *
from MoreaProperty import Property
from MoreaGrammar import MoreaGrammar
from Toolbox.toolbox import offset_string

__author__ = 'casanova'

import yaml


class MoreaFile(object):
    """A class that describes all content of a Morea .md file"""

    def __init__(self, path, warnings, parse_comments):
        self.path = path

        # Check that the .md file has 2 yaml documents in it and that the YAML can be parsed
        try:
            if not validate_basic_file_structure(self.path):
                raise CustomException("  Error: file " + self.path + " has too few '---' lines)")
        except Exception as e:
            err_msg = "  Error: YAML parse error for file " + self.path + "\n"
            err_msg += "        (jekyll may have been silent about this error!)\n"
            err_msg += offset_string(str(e), 4)
            raise CustomException(err_msg)


        # Get the content below the YAML
        self.non_yaml_contents = get_non_yaml_contents(path)

        #print "RAW YAML PARSING:"
        # print yaml.load(get_raw_front_matter(path))

        # Modify the YAML in a comment-preserving way
        try:
            commentified_front_matter = get_commentified_front_matter(path, warnings, parse_comments)
        except CustomException as e:
            err_msg = "  Error: unable to pre-process YAML content for comments for file " + self.path + "\n"
            err_msg += offset_string(str(e), 4)
            raise CustomException(err_msg)

        #print "COMENTIFIED_YAML = ", commentified_front_matter

        # Check for duplicate properties
        try:
            check_for_duplicate_entries(commentified_front_matter)
        except CustomException as e:
            err_msg = "  Error: duplicate entry error in file  " + self.path + "\n" + offset_string(str(e), 4)
            raise CustomException(err_msg)

        # Parse the YAML
        try:
            parsed_front_matter = yaml.load(commentified_front_matter)
        except Exception as e:
            err_msg = "  Error: unable to parse the pre-processed YAML content in file " + self.path + "\n"
            err_msg += offset_string(str(e), 4)
            err_msg += "\n\n" + get_raw_front_matter(self.path)
            err_msg += "\n\n" + commentified_front_matter
            raise CustomException(err_msg)

        if parsed_front_matter is None:
            raise CustomException("  Error: empty YAML front matter in file " + self.path + "\n")
        if type(parsed_front_matter) != dict:
            raise CustomException("  Error: non-dictionary-like YAML front matter in file " + self.path + "\n")


        # Convert every string to unicode
        parsed_front_matter = convert_to_unicode(parsed_front_matter)

        try:
            self.property_list = build_property_list(parsed_front_matter)
        except CustomException as e:
            err_msg = "  Error: unable to create property list from YAML in file " + self.path + "\n"
            err_msg += offset_string(unicode(e), 4)
            raise CustomException(err_msg)


        # OUTPUT FOR SHOW
        #print "Parsed content for file " + path + ":"
        #for p in self.property_list:
        #    self.property_list[p].display()

        return

    def typecheck(self):
        err_msg = ""

        # Check that all required properties are there, and that for each at least
        # one version is not commented out
        for name in MoreaGrammar.required_properties:
            if name not in self.property_list:
                err_msg += "  Error: missing required property '" + name + "'\n"
                continue
            if not self.property_list[name].has_uncommented_versions():
                err_msg += "  Error: missing required property '" + name + "' (only commented out)\n"
        if err_msg != "":
            raise CustomException(err_msg)

        # Check that each property is correct
        for name in self.property_list:

            try:
                MoreaGrammar.validate_property(name, self.property_list[name].versions)
            except CustomException as e:
                err_msg += unicode(e)

        if err_msg != "":
            raise CustomException(err_msg)

        return

    def get_value_of_scalar_required_property(self, name):
        try:
            prop = self.property_list[name]
            for version in prop.versions:
                if not version.commentedout:
                    if type(version.values) == tuple:
                        if not version.values[0]:
                            return version.values[1]
                    else:
                        for val in version.values:
                            if not val[0]:
                                return val[1]
        except Exception as e:
            raise CustomException(str(e))
        raise CustomException("  Value for property " + name + " not found!")

    def get_reference_list(self):
        reference_list = []
        for pname in self.property_list:
            if pname not in MoreaGrammar.morea_references:
                continue
            for version in self.property_list[pname].versions:
                if version.commentedout:
                    continue
                if type(version.values) == tuple:
                    value_list = [version.values]
                else:
                    value_list = version.values
                for val in value_list:
                    if val[0] is False:
                        reference_list.append([pname, val[1]])
        return reference_list


# HELPER FUNCTIONS BELOW #


def build_property_list(parsed_front_matter):
    property_list = {}
    # print "PARSED = ", parsed_front_matter

    # print "BUilDING PROPERTY LIST"
    for name in parsed_front_matter:

        # print "NAME=", name
        # get the uncommentified name and commentedout status
        (decommentified_name, commentedout) = decommentify(name)

        # print "DECOMMENTIFIED NAME--> ", decommentified_name, ",",  commentedout

        # get the value
        value = parsed_front_matter[name]

        # print "VALUE = ", value

        # Create the property object if not already created
        if decommentified_name not in property_list:
            property_list[decommentified_name] = Property(decommentified_name)

        # Add the version
        # print "ADDING A VERSION"
        try:
            property_list[decommentified_name].add_version(commentedout, value)
        except CustomException as e:
            # print "FAILED!!!"
            raise e

    # print "PROPERTY LIST="
    # for p in property_list:
    #    property_list[p].display()

    return property_list


def flattened_property_list(plist):
    new_plist = {}
    for name in plist:
        new_plist[name] = plist[name].flatten()
    return new_plist


def convert_to_unicode(dictionary):
    for key in dictionary:
        value = dictionary[key]
        dictionary[key] = recursive_unicodify(value)
    return dictionary


def recursive_unicodify(value):
    if type(value) == str:
        return unicode(value)
    elif type(value) == list:
        newlist = []
        for v in value:
            newlist.append(recursive_unicodify(v))
        return newlist
    else:
        return value




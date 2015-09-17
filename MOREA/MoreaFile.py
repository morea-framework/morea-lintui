from YamlParsingTools import *
from MoreaProperty import Property
from MoreaGrammar import MoreaGrammar
from Toolbox.toolbox import offset_string, morea_file_monitor

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

        # print "RAW YAML PARSING:"
        # print yaml.load(get_raw_front_matter(path))

        # Modify the YAML in a comment-preserving way
        try:
            commentified_front_matter = get_commentified_front_matter(path, warnings, parse_comments)
        except CustomException as e:
            err_msg = "  Error: unable to pre-process YAML content for comments for file " + self.path + "\n"
            err_msg += offset_string(str(e), 4)
            raise CustomException(err_msg)

        #print "COMMENTIFIED_YAML = ", commentified_front_matter

        # Check for duplicate properties
        try:
            check_for_duplicate_entries(commentified_front_matter, parse_comments)
        except CustomException as e:
            err_msg = "  Error: duplicate entry error in file  " + self.path + "\n" + offset_string(str(e), 4)
            exit(1)
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

        #print "PARSED_FRONT_MATTER:", parsed_front_matter
        # Build property list
        try:
            self.property_list = build_property_list(parsed_front_matter)
        except CustomException as e:
            err_msg = "  Error: unable to create property list from YAML in file " + self.path + "\n"
            err_msg += offset_string(unicode(e), 4)
            raise CustomException(err_msg)

        # OUTPUT FOR SHOW
        # print "PROPERTY LIST content for file " + path + ":"
        # for p in self.property_list:
        #     print "PROPERTY"
        #     self.property_list[p].display()

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

        # Check that each property is correctly specified
        for name in self.property_list:

            try:
                MoreaGrammar.validate_property(name, self.property_list[name].versions)
            except CustomException as e:
                err_msg += unicode(e)

        if err_msg != "":
            raise CustomException(err_msg)

        return

    # def has_uncommented_property(self, pname):
    #     if pname not in self.property_list:
    #         return False
    #     for version in self.property_list[pname].versions:
    #         if version.commented_out is False:
    #             return True
    #     return False

    def get_value_of_scalar_property(self, name):
        if name not in self.property_list:
            return None

        prop = self.property_list[name]
        if prop.grammar.multiple_values:
            raise CustomException("  Internal error: property " + name + " is not scalar!")
        else:
            return prop.get_first_uncommented_scalar_value()

    def set_value_of_scalar_property(self, name, value):

        try:
            prop = self.property_list[name]
            if prop.grammar.multiple_values:
                raise CustomException("  Internal error: property " + name + " is not scalar!")
            for version in prop.versions:
                if not version.commented_out:
                    if type(version.values) != list:
                        if not version.values.commented_out:
                            version.values.value = value
                        return
                    else:
                        for val in version.values:
                            if not val.commented_out:
                                val.val = value
                        return
        except Exception as e:
            raise CustomException(str(e))
        raise CustomException("  Value for property " + name + " not found!")

    def get_reference_list(self):
        reference_list = []
        for pname in self.property_list:
            if pname not in MoreaGrammar.morea_references:
                continue

            for version in self.property_list[pname].versions:
                #version.display()
                if version.commented_out:
                    continue
                if type(version.values) != list:
                    value_list = [version.values]
                else:
                    value_list = version.values
                for val in value_list:
                    if val.commented_out is False:
                        reference_list.append([pname, val.value])
        return reference_list

    def comment_out_all_references_to_id(self, morea_id):
        referencing_properties = ["morea_outcomes",
                                  "morea_readings",
                                  "morea_experiments",
                                  "morea_assessments",
                                  "morea_prerequisites",
                                  "morea_outcomes_assessed",
                                  ]
        for referencing_property in referencing_properties:
            self.property_list[referencing_property].comment_out_all_references_to_id(morea_id)

        return

    def save(self):

        # Don't do anything if the object hasn't changed
        if not morea_file_monitor.has_changed(self):
            return

        string = "---\n"
        for pname in MoreaGrammar.property_output_order:
            if pname in self.property_list:
                prop = self.property_list[pname]
                for version in prop.versions:
                    string += version.to_string()
        string += "---\n"
        string += self.non_yaml_contents

        # Saving the file
        f = open(self.path, 'w')
        f.write(string)
        f.close()
        return

    def display_properties(self):
        for p in self.property_list:
            self.property_list[p].display()


################################################################
#                   HELPER FUNCTIONS BELOW                     #
################################################################


def build_property_list(parsed_front_matter):
    property_list = {}
    # print "PARSED = ", parsed_front_matter

    # print "BUilDING PROPERTY LIST"
    for name in parsed_front_matter:

        # print "NAME=", name
        # get the uncommentified name and commented_out status
        (decommentified_name, commented_out) = decommentify(name)

        # Check that the property is for a known field
        if decommentified_name not in MoreaGrammar.property_syntaxes:
            raise CustomException("  Uknown property '" + name + "'")

        # print "DECOMMENTIFIED NAME--> ", decommentified_name, ",",  commented_out

        # get the value
        value = parsed_front_matter[name]

        # print "VALUE = ", value

        # Create the property object if not already created
        if decommentified_name not in property_list:
            #print "CREATING A NEW PROPERTY FOR", decommentified_name
            property_list[decommentified_name] = Property(decommentified_name)

        # Add the version
        # print "ADDING A VERSION"
        try:
            #print "ADDING A VERSION TO PROPERTY ", decommentified_name
            property_list[decommentified_name].create_and_add_version(commented_out, value)
        except CustomException as e:
            raise e

    # print "\n********************\nPROPERTY LIST="
    # for p in property_list:
    #     print "PROPERTY:"
    #     property_list[p].display()

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

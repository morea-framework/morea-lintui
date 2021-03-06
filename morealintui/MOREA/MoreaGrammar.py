from morealintui.Toolbox.toolbox import CustomException, my_str

__author__ = 'casanova'


class PropertySyntax(object):
    """A class that describes the nature of what's allowed for a morea property"""

    def __init__(self, name, multiple_values, data_type, allowed_values, required, quoted):
        self.name = name  # string
        self.multiple_values = multiple_values  # boolean
        self.data_type = data_type  # type
        self.allowed_values = allowed_values  # list
        self.required = required  # boolean
        self.quoted = quoted  # boolean
        return


class MoreaGrammar(object):
    """A class that encodesuseful constants"""

    morea_types = ["home", "footer", "module", "outcome", "reading", "experience", "assessment",
                   "overview_assessments", "overview_experiences", "overview_outcomes",
                   "overview_modules", "overview_readings", "prerequisite"]

    morea_references = ["morea_outcomes", "morea_readings", "morea_experiences", "morea_assessments",
                        "morea_outcomes_assessed"]

    property_output_order = ["morea_id",
                             "morea_type",
                             "title",
                             "published",
                             "morea_coming_soon",
                             "morea_highlight",
                             "morea_start_date",
                             "morea_end_date",
                             "morea_summary",
                             "morea_outcomes",
                             "morea_readings",
                             "morea_experiences",
                             "morea_assessments",
                             "morea_sort_order",
                             "morea_url",
                             "morea_icon_url",
                             "morea_prerequisites",
                             "morea_outcomes_assessed",
                             "morea_labels",
                             "morea_chartjs_caption",
                             "morea_chartjs_labels",
                             "morea_chartjs_data"
                             ]

    property_syntaxes = {"morea_type": PropertySyntax(name="morea_type", multiple_values=False, data_type=unicode,
                                                      allowed_values=morea_types,
                                                      required=True, quoted=False),
                         "title": PropertySyntax(name="title", multiple_values=False, data_type=unicode,
                                                 allowed_values=None, required=True, quoted=True),
                         "published": PropertySyntax(name="published", multiple_values=False, data_type=bool,
                                                     allowed_values=[True, False], required=True, quoted=False),
                         "morea_highlight": PropertySyntax(name="morea_highlight", multiple_values=False,
                                                           data_type=bool,
                                                           allowed_values=[True, False], required=False, quoted=False),
                         "morea_coming_soon": PropertySyntax(name="morea_coming_soon", multiple_values=False,
                                                             data_type=bool,
                                                             allowed_values=[True, False], required=False,
                                                             quoted=False),
                         "morea_id": PropertySyntax(name="morea_id", multiple_values=False, data_type=unicode,
                                                    allowed_values=None,
                                                    required=True, quoted=False),
                         "morea_outcomes": PropertySyntax(name="morea_outcomes", multiple_values=True,
                                                          data_type=unicode,
                                                          allowed_values=None,
                                                          required=False, quoted=False),
                         "morea_experiences": PropertySyntax(name="morea_experiences", multiple_values=True,
                                                             data_type=unicode, allowed_values=None,
                                                             required=False, quoted=False),
                         "morea_assessments": PropertySyntax(name="morea_assessments", multiple_values=True,
                                                             data_type=unicode, allowed_values=None,
                                                             required=False, quoted=False),
                         "morea_readings": PropertySyntax(name="morea_readings", multiple_values=True,
                                                          data_type=unicode,
                                                          allowed_values=None,
                                                          required=False, quoted=False),
                         "morea_icon_url": PropertySyntax(name="morea_icon_url", multiple_values=False,
                                                          data_type=unicode,
                                                          allowed_values=None,
                                                          required=False, quoted=False),
                         "morea_url": PropertySyntax(name="morea_url", multiple_values=False, data_type=unicode,
                                                     allowed_values=None,
                                                     required=False, quoted=False),
                         "morea_sort_order": PropertySyntax(name="morea_sort_order", multiple_values=False,
                                                            data_type=int, allowed_values=None,
                                                            required=False, quoted=False),
                         "morea_prerequisites": PropertySyntax(name="morea_prerequisites", multiple_values=True,
                                                               data_type=unicode, allowed_values=None,
                                                               required=False, quoted=False),
                         "morea_summary": PropertySyntax(name="morea_summary", multiple_values=False, data_type=unicode,
                                                         allowed_values=None,
                                                         required=False, quoted=True),
                         "morea_labels": PropertySyntax(name="morea_labels", multiple_values=True, data_type=unicode,
                                                        allowed_values=None,
                                                        required=False, quoted=True),
                         "morea_outcomes_assessed": PropertySyntax(name="morea_outcomes_assessed", multiple_values=True,
                                                                   data_type=unicode,
                                                                   allowed_values=None,
                                                                   required=False, quoted=False),
                         "morea_start_date": PropertySyntax(name="morea_start_date", multiple_values=False,
                                                            data_type=unicode, allowed_values=None,
                                                            required=False, quoted=True),
                         "morea_end_date": PropertySyntax(name="morea_end_date", multiple_values=False,
                                                          data_type=unicode,
                                                          allowed_values=None,
                                                          required=False, quoted=True),
                         "morea_chartjs_caption": PropertySyntax(name="morea_chartjs_caption", multiple_values=False,
                                                                 data_type=unicode,
                                                                 allowed_values=None,
                                                                 required=False, quoted=True),
                         "morea_chartjs_labels": PropertySyntax(name="morea_chartjs_labels", multiple_values=False,
                                                                data_type=unicode,
                                                                allowed_values=None,
                                                                required=False, quoted=True),
                         "morea_chartjs_data": PropertySyntax(name="morea_chartjs_data", multiple_values=False,
                                                              data_type=unicode, allowed_values=None,
                                                              required=False, quoted=True)
                         }

    required_properties = [x for x in property_syntaxes.keys() if property_syntaxes[x].required is True]

    @staticmethod
    def is_valid_reference(label, morea_id):
        if label == "morea_outcomes":
            if morea_id != "outcome":
                return False
        elif label == "morea_outcomes_assessed":
            if morea_id != "outcome":
                return False
        elif label == "morea_readings":
            if morea_id != "reading":
                return False
        elif label == "morea_experiences":
            if morea_id != "experience":
                return False
        elif label == "morea_assessments":
            if morea_id != "assessment":
                return False
        else:
            raise CustomException("Internal Error: Unknown label")
        return True

    @staticmethod
    def get_reference(morea_type):
        # WARNING: DOES NOT DEAL WITH MOREA_ASSESSED_OUTCOMES
        if morea_type == "outcome":
            return "morea_outcomes"
        elif morea_type == "reading":
            return "morea_readings"
        elif morea_type == "experience":
            return "morea_experiences"
        elif morea_type == "assessment":
            return "morea_assessments"
        else:
            return None

    @staticmethod
    def validate_property(name, versions):
        err_msg = ""

        # Try to find the syntax
        try:
            syntax = MoreaGrammar.property_syntaxes[name]
        except KeyError:
            err_msg += "  Error: unknown property " + name + "\n"
            raise CustomException(err_msg)

        # Look at all the versions
        for version in versions:
            try:
                MoreaGrammar.validate_version(syntax, version)
            except CustomException as e:
                err_msg += unicode(e)

        # Detect missing required property
        if syntax.required:
            provided = False
            for version in versions:
                # list-if a single values, temporarily
                if type(version.values) != list:
                    value_list = [version.values]
                else:
                    value_list = version.values
                for v in value_list:
                    if v.commented_out is False and v.value is not None:
                        provided = True
                    else:
                        pass
            if not provided:
                err_msg += "  Error: missing required property " + syntax.name + "\n"

        if err_msg != "":
            raise CustomException(err_msg)

        return

    @staticmethod
    def validate_version(syntax, version):
        err_msg = ""

        # version.display()
        # check for multiple vs. single value
        if version.num_of_uncommented_values() > 1 and not syntax.multiple_values:
            err_msg += "  Error: property " + syntax.name + " can have only one value" + "\n"

        # list-if a single values, temporarily
        if type(version.values) != list:
            value_list = [version.values]
        else:
            value_list = version.values

        # Check for value types
        for v in value_list:
            if v.value is not None and type(v.value) != syntax.data_type:
                err_msg += "  Error: value '" + my_str(
                    v.value) + "' has invalid type for property " + syntax.name + "\n"

        # Check for allowed values
        if syntax.allowed_values is not None:
            for v in value_list:
                if v.value is not None:
                    if v.value not in syntax.allowed_values:
                        err_msg += "  Error: disallowed value '" + str(v.value) + "' for property " + \
                                   syntax.name + "\n" + "         (allowed values: " + \
                                   str(syntax.allowed_values) + ")"

        if err_msg != "":
            raise CustomException(err_msg)

        return

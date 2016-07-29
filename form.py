"""
    Form and form fields data classes
"""


class Field(object):
    """
        Field data
    """

    def __init__(self, name, field_type, value):
        self.name = name
        self.field_type = field_type
        self.value = value

    def get_name(self):
        """
            Returns field name
        """

        return self.name

    def get_type(self):
        """
            Return field type
        """

        return self.field_type

    def get_value(self):
        """
            Returns field value
        """

        return self.value


class Form(object):
    """
        Form data
    """

    def __init__(self, form_id, fields, action, method):
        self.form_id = form_id
        self.fields = fields
        self.action = action
        self.method = method

    def get_id(self):
        """
            Returns form id
        """

        return self.form_id

    def get_fields(self):
        """
            Returns form fields
        """

        return self.fields

    def get_action(self):
        """
            Returns form action
        """

        return self.action

    def get_method(self):
        """
            Returns form method
        """

        return self.method

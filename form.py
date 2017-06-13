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


class Form(object):
    """
        Form data
    """

    def __init__(self, url, fields, action, method):
        self.url = url
        self.fields = fields
        self.action = action
        self.method = method

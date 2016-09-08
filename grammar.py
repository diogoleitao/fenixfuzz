"""
    Grammar stuff
"""

import random
import string

import globalvars
from form import Field


CHARSETS = {
    # Alphanumeric, symbols and whitespace characters
    "all": string.printable,

    # Alphanumeric and symbols
    "no-white": string.ascii_letters + string.digits + string.punctuation,

    # Alphanumeric
    "alpha": string.ascii_letters + string.digits,

    # Characters
    "char": string.ascii_letters,

    # Numbers
    "num": string.digits
}

# FUZZABLE_TYPES = ["text", "number", "textarea", "radio", "checkbox", "search", "date"]  # TODO

def generate_strings(charset, length):
    """
        Returns a string with a given length containing a subset of
        characters from a given charset.
    """
    return ''.join(random.choice(charset) for i in range(length))

def generate(field_type):
    """
        Returns an array of fuzz pattern strings with variable lengths,
        ranging from min_length to max_length. Each string is made up of a
        subset of characters, based on the charset given as input.
    """
    maximum = globalvars.MAXIMUM
    minimum = globalvars.MINIMUM

    for i in range(minimum, maximum + 1):
        charset = globalvars.CHARSET
        if field_type is not None:
            charset = CHARSETS[field_type]
        return generate_strings(charset, i)


def process_field(form, field):
    """
        TODO
    """
    try:
        field_name = field.get("name")
        field_type = field.get("type")
        field_value = field.get("value")

        if field_type == "hidden":
            return Field(field_name, field_type, field_value)

        elif field_type == "text":
            try:
                if field_name != "j_captcha_response":
                    fuzz_pattern = ""
                    name = field_name.split(":")
                    final_name = name[len(name) - 1]

                    if final_name == "studentNumber":
                        fuzz_pattern = "19"

                    elif final_name == "documentIdNumber":
                        fuzz_pattern = "0123456789"

                    elif final_name == "email":
                        fuzz_pattern = "mail@ist.utl.pt"
                    return Field(field_name, field_type, fuzz_pattern)

            except AttributeError:
                # Some input attributes are blank or aren't of type
                # 'string', which can't be coerced; so, we just ignore
                # the errors.
                pass

        elif field_type == "radio":
            radio_options = form.find_all("input", {"type": "radio"})
            selected = radio_options[random.randrange(len(radio_options))]
            return Field(selected.get("name"), field_type, selected.get("value"))

        elif field_type == "checkbox":
            checkboxes = form.find_all("input", {"type": "checkbox"})
            selected = checkboxes[random.randrange(len(checkboxes))]

            if selected.has_attr("value"):
                return Field(selected.get("name"), field_type, selected.get("value"))

            else:
                return Field(selected.get("name"), field_type, "on")

        elif field_type == "date":
            pass

        elif field_type == "email":
            return Field(field_name, field_type, "example@example.com")

        elif field_type == "search":
            pass

    except AttributeError:
        # Some input attributes are blank or aren't of type 'string', which
        # can't be coerced; so, we just ignore the errors.
        pass

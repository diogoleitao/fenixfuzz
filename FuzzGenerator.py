import random
import string

import globalvars


class FuzzGenerator(object):
    """Generator"""

    field_types_to_charset = {
        "text": "char"
    }

    charsets = {
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

    def __init__(self):
        return

    def generate_strings(self, charset, length):
        """
            Returns a string with a given length containing a subset of
            characters from a given charset.
        """
        return ''.join(random.choice(charset) for i in range(length))

    def generate(self, field_type, max_length, min_length):
        """
            Returns an array of fuzz pattern strings with variable lengths,
            ranging from min_length to max_length. Each string is made up of a
            subset of characters, based on the charset given as input.
        """
        if globalvars.GMODE == "generation":
            maximum = globalvars.MAX_LENGTH
            minimum = globalvars.MIN_LENGTH

            if max_length is not None:
                maximum = max_length
            if min_length is not None:
                minimum = min_length

            for i in range(minimum, maximum + 1):
                charset = globalvars.CHARSET
                if field_type is not None:
                    charset = self.charsets[self.field_types_to_charset[field_type]]
                return self.generate_strings(charset, i)

        # if globalvars.GMODE == "generation":
        #     fuzz_patterns = []
        #     for i in range(globalvars.MIN_LENGTH, globalvars.MAX_LENGTH + 1):
        #         fuzz_patterns.append(self.generate_strings(globalvars.CHARSET, i))
        #     globalvars.GARBAGE_STRINGS = fuzz_patterns
        # elif globalvars.GMODE == "mutation":
        #     known_bad = []
        #     with open("bad_input", "r") as bad_input_file:
        #         known_bad.append(bad_input_file.readline)
        #     # DO MUTATION ON ACQUIRED STRING

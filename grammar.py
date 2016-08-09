"""
    Grammar stuff
"""
import random
import string

import globalvars


class FuzzGenerator(object):
    """
        Generator
    """

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

    def generate_strings(self, charset, length):
        """
            Returns a string with a given length containing a subset of
            characters from a given charset.
        """
        return ''.join(random.choice(charset) for i in range(length))

    def generate(self, field_type):
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
                charset = self.charsets[field_type]
            return self.generate_strings(charset, i)

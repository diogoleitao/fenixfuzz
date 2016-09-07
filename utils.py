"""
    Global functions and message templates
"""

import json
import os.path
import sys

import globalvars
import scraping

# The help message to be displayed. It is "oddly" formatted so it is easier to
# see how the final message will look (instead of using \t and \n characters to
# align everything).
HELP_TEXT = "\
USAGE:\n\
        parser.py -f [FILE] [OPTIONS]\n\n\
OPTIONS:\n\
-f, --file:\n\
        Path to the .properties file needed to configure the fuzzer.\n\
        Example: /path/to/fenixfuzz.properties.\n\n\
-l, --url:\n\
        Override starting URL, to test a specific page.\n\
        Example: <local_instance>/page.do.\n\n\
-i, --iter:\n\
        How many times the tool will fuzz Fenix, reusing the inputs with the best results.\n\
        Defaults to 1 if not specified.\n\
        Example: 2.\n\n\
-h, --help:\n\
        Shows this text."

ERROR_MESSAGE = "Please check that a value was correctly specified for the {0} option."

NO_FORM_ACTION = "Form has no explicit action, so can't be tested."


def parse_command_line():
    """
        Parses the command line options and prints the errors, if any occur.
    """

    if "-h" in sys.argv or "--help" in sys.argv:
        terminate(HELP_TEXT, 0)

    if "-f" in sys.argv or "--file" in sys.argv:
        try:
            path_index = sys.argv.index("-f") + 1
        except ValueError:
            path_index = sys.argv.index("--file") + 1
        try:
            path = sys.argv[path_index]
            if not os.path.isfile(path):
                terminate(ERROR_MESSAGE.format("-f/--file"), 1)
        except IndexError:
            terminate(ERROR_MESSAGE.format("-f/--file"), 1)
    else:
        terminate("-f/--file option not specified", 1)

    if "-l" in sys.argv or "--url" in sys.argv:
        try:
            url_index = sys.argv.index("-l") + 1
        except ValueError:
            url_index = sys.argv.index("--url") + 1
        try:
            globalvars.START_PAGE = sys.argv[url_index]
        except IndexError:
            terminate(ERROR_MESSAGE.format("-l/--url"), 1)
    elif "-i" in sys.argv or "--iter" in sys.argv:
        try:
            iter_index = sys.argv.index("-i") + 1
        except ValueError:
            iter_index = sys.argv.index("--iter") + 1
        try:
            globalvars.ITERATIONS = int(sys.argv[iter_index])
        except ValueError:
            terminate(ERROR_MESSAGE.format("-i/--iter"), 1)
    return path


def read_properties_file(path, sep=" = ", comment_char="#"):
    """
        Parses the .properties file's values. If any error occurs, it prints a
        message and kills the program.
    """

    try:
        props = {}
        with open(path, "r") as properties_file:
            for line in properties_file:
                line = line.strip()
                if line and not line.startswith(comment_char):
                    key_value = line.split(sep)
                    props[key_value[0].strip()] = key_value[1].strip("\" \t")
        return props
    except OSError:
        terminate(ERROR_MESSAGE.format("-f/--file"), 1)


def read_exclude_urls_file():
    """
        Parses the contents of the file containing the URLs to be excluded while
        crawling and adds them to the global variable EXCLUDE_URLS
    """

    with open(globalvars.EXCLUDE_URLS_FILE, "r") as exclude_patterns_file:
        scraping.EXCLUDE_URLS += json.loads(exclude_patterns_file.read())


def read_fenixfuzz_model_file():
    """
        Parses the contents of the file describing the grammar and creates the
        appropriate associations between the field types and the regular
        expressions to be used.
    """

    with open(globalvars.FENIXFUZZ_MODEL_FILE, "r") as ffm_file:
        return json.loads(ffm_file.read())


def terminate(message, code):
    """
        Prints a message and exits the main program with the given error code.
    """

    if code == 1:
        printf("ERROR:\n\t" + message)
    else:
        printf(message)
    sys.exit(code)


def printf(message, end="\n"):
    """
        An alternative to Python's builtin print function.
    """

    sys.stdout.write(str(message) + end)
    sys.stdout.flush()

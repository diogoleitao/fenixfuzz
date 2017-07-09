"""
    I/O handlers and message templates
"""

import json
import os.path
import sys


# The help message to be displayed. It is "oddly" formatted so it is easier to see how the final
# message will look (instead of using \t to align everything).
HELP_TEXT = "\
USAGE:\n\
        parser.py -f [FILE] [OPTIONS]\n\n\
        -f, --file:\n\
            Path to the .properties file needed to configure the fuzzer.\n\
            Example: /path/to/fenixfuzz.properties.\n\n\
OPTIONS:\n\
        -j, --json-report:\n\
            Override default path (output/report.json) for the JSON report file.\n\
            Example: /path/to/report.json.\n\n\
        -g, --generate-html-report:\n\
            If present, an HTML report file will be generated.\n\
            The report file will be created in the \"output\" directory (unless overridden).\n\n\
        -r, --html-report:\n\
            Override default path (output/report.html) for the HTML report file.\n\
            Example: /path/to/report.html.\n\n\
        -h, --help:\n\
            Print this text.\n"

ERROR_MESSAGE = "Please check that a value was correctly specified for the {0} option."

NO_FORM_ACTION = "Form has no explicit action (destination URL), so it can't be tested."


def parse_command_line():
    """
        Parses the command line options and prints the errors, if any occur.
    """

    if "-h" in sys.argv or "--help" in sys.argv:
        terminate(HELP_TEXT, 0)

    if "-f" in sys.argv or "--file" in sys.argv:
        try:
            file_index = sys.argv.index("-f") + 1
        except ValueError:
            file_index = sys.argv.index("--file") + 1

        try:
            properties_file = sys.argv[file_index]
            if not os.path.isfile(properties_file):
                terminate(ERROR_MESSAGE.format("-f/--file"), 1)
        except IndexError:
            terminate(ERROR_MESSAGE.format("-f/--file"), 1)
    else:
        terminate("-f/--file option not specified", 1)

    if "-j" in sys.argv or "--json-report" in sys.argv:
        try:
            json_report_index = sys.argv.index("-j") + 1
        except ValueError:
            json_report_index = sys.argv.index("--json-report") + 1

        try:
            json_report_file = sys.argv[json_report_index]
        except IndexError:
            terminate(ERROR_MESSAGE.format("-j/--json-report"), 1)
    else:
        json_report_file = None

    generate_html_report = True if "-g" in sys.argv or "--generate-html-report" in sys.argv else False

    if generate_html_report and ("-r" in sys.argv or "--html-report" in sys.argv):
        try:
            html_report_index = sys.argv.index("-r") + 1
        except ValueError:
            html_report_index = sys.argv.index("--html-report") + 1

        try:
            html_report_file = sys.argv[html_report_index]
        except IndexError:
            terminate(ERROR_MESSAGE.format("-r/--html-report"), 1)
    else:
        html_report_file = None

    return properties_file, json_report_file, generate_html_report, html_report_file


def read_properties_file(path, sep="=", comment_char="#"):
    """
        Parses the .properties file's values. If any error occurs, it prints a message and kills the
        program.
    """

    try:
        properties = {}
        with open(path, "r") as properties_file:
            for line in properties_file:
                line = line.strip()

                if line and not line.startswith(comment_char):
                    key_value = line.split(sep)
                    properties[key_value[0].strip()] = key_value[1].strip()
        return properties
    except OSError:
        terminate(ERROR_MESSAGE.format("-f/--file"), 1)


def read_url_patterns_file(url_patterns_path):
    """
        Loads the URL patterns from the corresponding file
    """

    with open(url_patterns_path, "r") as url_patterns_file:
        json_data = json.loads(url_patterns_file.read())
        return json_data["exclude"], json_data["sample"]


def read_fenixfuzz_model_file(ffm_path):
    """
        Parses the contents of the file describing the grammar and creates the appropriate
        associations between the field types and the regular expressions to be used.
    """

    with open(ffm_path, "r") as ffm_file:
        return json.loads(ffm_file.read())


def terminate(message, code):
    """
        Prints a message and exits the main program with the given error code.
    """

    print("ERROR:\n\t" + message if code == 1 else message)
    sys.exit(code)

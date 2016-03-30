import string
import random
import requests
import sys
import re
from bs4 import BeautifulSoup


# Prettier exit function
def quit(code):
    sys.exit(code)


# Returns a string with a given length containing a set of random characters
def generateStrings(charset, length):
    return ''.join(random.choice(charset) for i in range(length))


# Returns an array of fuzz patterns with variable lengths, ranging from min_length to max_length
# Each string is made up of a subset of characters, based on the charset given as input
def generateFuzzPatterns(mode, minimum, maximum):
    strings = []
    for i in range(minimum, maximum + 1):
        strings.append(generateStrings(mode, i))
    return strings


def printFinalResults():
    return


# Parses command line arguments to:
#   - set fuzz pattern's minimum and maximum length
#   - set fuzz pattern's generation mode
#   - check if FenixEdu API is to be tested as well
#   - retrieve API version (when the API is being tested)
#   - set the charset used for the fuzz pattern generation
#   - choose the type of user to access FenixEdu: student, teacher or system administrator
# If any errors occur, they are printed out and the main program terminates
def parseInput():
    default_warning = "Option {0} was not specified; using default value: {1}"

    minimum = 1
    maximum = 20
    mode = "generation"
    api = False
    charset = string.letters + string.digits
    version = 1
    user = "student"
    final_error = ""

    if "-h" in sys.argv:
        print "Usage:\n\tfenixfuzz.py -min minimum  -max maximum  -gmode generation_mode  -api  -v version  -c charset  -u user"
        print "Options:"
        print "\t-min:\tminimum fuzz pattern length.\n\t\tAccepted values: positive integers.\n\t\tDefault value: 1.\n"
        print "\t-max:\tmaximum fuzz pattern length.\n\t\tAccepted values: positive integers.\n\t\tDefault value: 20.\n"
        print "\t-gmode:\tfuzz pattern generation mode.\n\t\tAccepted values: generation and mutation.\n\t\tDefault value: generation.\n"
        print "\t-api:\tif specified, the fuzzer also tests the FenixEdu API.\n"
        print "\t-v:\tspecifies the API version (useless if -api is not specified).\n\t\tAccepted values: positive integers.\n\t\tDefault value: 1.\n"
        print "\t-c:\tcharset used for the fuzz patterns (a combination of letters, digits, punctuation/symbols and whitespace characters).\n\t\tAccepted values: all, no-white, alpha, char or num.\n\t\tDefault value: alpha.\n"
        print "\t-u:\tuser role used for the login process.\n\t\tAccepted values: student, teacher or sysadm.\n\t\tDefault value: ?.\n"
        quit(0)
    else:
        if "-min" in sys.argv:
            min_index = sys.argv.index("-min") + 1
            try:
                minimum = int(sys.argv[min_index])
                if minimum < 0:
                    final_error += "\n\t-min should be greater than or equal to zero."
            except ValueError:
                final_error += "\n\t-min should be an integer."
        else:
            print default_warning.format("-min", str(minimum))

        if "-max" in sys.argv:
            max_index = sys.argv.index("-max") + 1
            try:
                maximum = int(sys.argv[max_index])
                if maximum < 1:
                    final_error += "\n\t-max should be greater than zero."
                elif maximum < minimum:
                    final_error += "\n\t-max should be greater than -min."
            except ValueError:
                final_error += "\n\t-max should be an integer."
        else:
            print default_warning.format("-max", str(maximum))

        if "-gmode" in sys.argv:
            gmode_index = sys.argv.index("-gmode") + 1
            mode = sys.argv[gmode_index]
            if mode == "generation" or mode == "mutation":
                pass
            else:
                final_error += "\n\t-gmode should be either generation or mutation."
        else:
            print default_warning.format("-gmode", mode)

        if "-api" in sys.argv:
            api = True
            if "-v" in sys.argv:
                api_version_index = sys.argv.index("-v") + 1
                try:
                    version = int(sys.argv[api_version_index])
                except ValueError:
                    final_error += "\n\t-v should be an integer."
            else:
                print default_warning.format("-v", str(version))
        else:
            print default_warning.format("-api", str(api))

        if "-c" in sys.argv:
            charset_index = sys.argv.index("-c") + 1
            charset = sys.argv[charset_index]
            all_charsets = {
                # Alphanumeric, symbols and whitespace characters
                "all": string.printable,

                # Alphanumeric and symbols
                "no-white": string.letters + string.digits + string.punctuation,

                # Alphanumeric
                "alpha": string.letters + string.digits,

                # Characters
                "char": string.letters,

                # Numbers
                "num": string.digits
            }

            try:
                charset = all_charsets[charset]
            except KeyError:
                final_error += "\n\t-c should be either all, no-white, alpha, char or num."
        else:
            print default_warning.format("-c", charset)

        if "-u" in sys.argv:
            user_index = sys.argv.index("-u") + 1
            user = sys.argv[user_index]
            if user == "student" or user == "teacher" or user == "sysadm":
                pass
            else:
                final_error += "\n\t-u should be either student, teacher or sysadm."
        else:
            print default_warning.format("-u", user)

        if len(final_error) > 0:
            final_error = "Error(s):" + final_error
            print final_error
            quit(1)
        else:
            return minimum, maximum, mode, api, charset, version, user


# Fuzzes the FenixEdu API and prints the sent requests
def fuzzFenixeduAPI(fuzz_patterns, version):
    fenixEdu_URL_api = "http://fenixedu.org/dev/api/index.html"
    get_endpoints = []
    put_endpoints = []

    fenixedu_page = requests.get(fenixEdu_URL_api).text
    html_tree = BeautifulSoup(fenixedu_page, 'html.parser')
    endpoints_list = html_tree.find_all('a')
    for endpoint in endpoints_list:
        real_endpoint = endpoint.getText()
        if "GET" in real_endpoint:
            get_endpoints.append(real_endpoint[4:])
        elif "PUT" in real_endpoint:
            put_endpoints.append(real_endpoint[4:])

    base_url = "https://fenix.tecnico.ulisboa.pt/api/fenix/v" + str(version)
    server_error_pattern = re.compile("^5[0-9][0-9]$")

    for endpoint in get_endpoints:
        if "{id}" in endpoint:
            for fuzz_pattern in fuzz_patterns:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.get(base_url + final_endpoint)
                if server_error_pattern.match(str(http_request.status_code)):
                    print str(http_request.status_code) + " " + final_endpoint
        else:
            # Endpoints without parameters can't be fuzzed
            pass

    for endpoint in put_endpoints:
        if "{id}" in endpoint:
            for fuzz_pattern in fuzz_patterns:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.put(base_url + final_endpoint)
                if server_error_pattern.match(str(http_request.status_code)):
                    print str(http_request.status_code) + " " + final_endpoint
        else:
            # Endpoints without parameters can't be fuzzed
            pass


# Fuzzes the FenixEdu pages
def fuzzFenixedu(fuzz_patterns):
    fenixEdu_starfleet = "localhost:8080/starfleet/login"

    # It should iterate through the crawled pages
    current_page = fenixEdu_starfleet

    # test.py

    # PAGE CRAWLER
    page = requests.get(current_page).text
    html_tree = BeautifulSoup(page, 'html_parser')
    all_links = html_tree.find_all('a')
    parsed_links = []
    for link in all_links:
        anchor = link.get("href")
        if "http://localhost:8080/" in anchor:
            parsed_links.append(anchor)

    # FORM CRAWLER
    all_forms = html_tree.find_all('form')
    forms_and_fields = {}
    forms_and_actions = {}
    for form in all_forms:
        forms_and_actions[form] = form.get("action")

        inputs = []
        for inpt in form.find_all("input"):
            if inpt.get("type") != "hidden":
                inputs.append(inpt)
        forms_and_fields[form] = inputs


# Main program
def _main():
    """
        Since Python only allows variables to be defined and not declared,
        all of them are assigned a "default" value, but that does not reflect
        its final value (that is, the value assigned when the script is
        running). This is avoided with the parseInput() function (see its
        documentation).
    """

    # Minimum fuzz pattern string length
    min_length = 0
    # Maximum fuzz pattern string length
    max_length = 0
    # Fuzz pattern generation mode
    gmode = ""
    # If True, tests FenixEdu API
    test_api = False
    # Charset command line option
    charset = ""
    # List of generated fuzz patterns
    garbage_strings = []
    # API version (only used if test_api is specified, to build the request URL)
    api_version = 0
    # User role to perform login
    user_role = ""

    parsed_input_values = parseInput()

    min_length = parsed_input_values[0]
    max_length = parsed_input_values[1]
    gmode = parsed_input_values[2]
    test_api = parsed_input_values[3]
    charset = parsed_input_values[4]
    api_version = parsed_input_values[5]
    user_role = parsed_input_values[6]

    garbage_strings = generateFuzzPatterns(charset, min_length, max_length)

    if test_api:
        fuzzFenixeduAPI(garbage_strings, api_version)

    # fuzzFenixedu(garbage_strings)

    printFinalResults()


# Standard Python 'main' function invocation
if __name__ == '__main__':
    _main()

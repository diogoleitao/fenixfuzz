import string
import random
import requests
import sys
import re
from bs4 import BeautifulSoup


# "Prettier" exit function.
def quit(code):
    sys.exit(code)


# Returns a string with a given length containing a subset of characters from
# a given charset.
def generateStrings(charset, length):
    return ''.join(random.choice(charset) for i in range(length))


# Returns an array of fuzz pattern strings with variable lengths, ranging from
# min_length to max_length. Each string is made up of a subset of characters,
# based on the charset given as input.
def generateFuzzPatterns(charset, minimum, maximum, gmode):
    if gmode == "generation":
        strings = []
        for i in range(minimum, maximum + 1):
            strings.append(generateStrings(charset, i))
        return strings
    elif gmode == "mutation":
        known_bad = []
        with open("bad_input", "r") as bad_input_file:
            known_bad.append(bad_input_file.readline)
        # DO MUTATION ON ACQUIRED STRING


# NEEDS TO BE DETERMINED IN WHAT WAY IT IS PRESENTED AND WHAT INFORMATION IS
# IMPORTANT TO BE SHOWN TO THE FENIXEDU DEVELOPERS
def printFinalResults():
    return


# Parses command line arguments to:
#   - set fuzz pattern's minimum and maximum length;
#   - set fuzz pattern's generation mode;
#   - check if FenixEdu API is to be tested as well;
#   - retrieve API version (for when the API is being tested);
#   - set the charset used for the fuzz pattern generation;
#   - choose the type of user to access FenixEdu: student, teacher or system
#     administrator;
# Some arguments have default values; so, if they're not specified, each option
# will fall back to its default value. Note however that some options must be
# specified, and thus, don't have default values.
# If any errors occur, they are printed out and the main program terminates.
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
        print "\t-v:\tspecifies the API version.\n\t\tAccepted values: positive integers.\n\t\tDefault value: 1.\n"
        print "\t-c:\tcharset used for the fuzz patterns (letters, digits, punctuation/symbols, whitespace characters).\n\t\tAccepted values: all, no-white, alpha, char or num.\n\t\tDefault value: none.\n"
        print "\t-u:\tuser role used for the login process.\n\t\tAccepted values: student, teacher or system administrator.\n\t\tDefault value: none.\n"
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
            final_error += "\n\t-c must be specified (all, no-white, alpha, char, num)."

        if "-u" in sys.argv:
            user_index = sys.argv.index("-u") + 1
            user = sys.argv[user_index]
            teacher = random.randrange(2, 15, 1)
            student = random.randrange(16, 30, 1)
            all_users = {
                'sysadm': 'SA1',
                'teacher': 'SA' + teacher,
                'student': 'SA' + student
            }
            try:
                user = all_users[user]
            except KeyError:
                final_error += "\n\t-u should be either student, teacher or sysadm."
        else:
            final_error += "\n\t-u must be specified (student, teacher, sysadm)."

        if len(final_error) > 0:
            final_error = "Error(s):" + final_error
            print final_error
            quit(1)
        else:
            return minimum, maximum, mode, api, charset, version, user


# Fuzzes the FenixEdu API and prints the requests sent which triggered a server
# side error. The API endpoints are retrieved via its documentation webpage, by
# parsing the bullet list and retrieving only the endpoint (e.g.: /courses/{id}).
# The final URL used for the request is built using th base url, concatenated
# with the current endpoint being tested and with the current fuzz pattern.
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


# Performs login at the local Fenix instance and returns a dictionary
# containing the cookies needed for each request.
def doLogin(user):
    request_url = "http://localhost:8080/starfleet/api/bennu-core/profile/login"

    response = requests.post(request_url, data={'username': user, 'password': ''})
    cookie_values = response.headers.get('set-cookie').replace(';', '').replace(',', '').split(' ')
    context_path = cookie_values[0].split('=')[1]
    cookie = cookie_values[2].split('=')[1]

    cookies = {
        'JSESSION_ID': cookie,
        'contextPath': context_path
    }

    return cookies


# Fuzzes the FenixEdu pages
# TODO: add details
def fuzzFenixedu(fuzz_patterns, user):
    COOKIES = doLogin(user)

    landing_page_url = "http://localhost:8080" + COOKIES['contextPath'] + "/home.do"
    landing_page = requests.post(landing_page_url, cookies=COOKIES).text
    landing_page_html_tree = BeautifulSoup(landing_page, 'html.parser')

    all_forms = landing_page_html_tree.find_all('form')
    forms_and_inputs = {}
    forms_and_actions = {}
    if len(all_forms) != 0:
        for form in all_forms:
            forms_and_actions[form] = form.get("action")
            inputs_and_types = {}
            for inpt in form.find_all("input"):
                if inpt.get("type") != "hidden":
                    inputs_and_types[inpt] = type
            forms_and_inputs[form] = inputs_and_types


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
    MIN_LENGTH = 0
    # Maximum fuzz pattern string length
    MAX_LENGTH = 0
    # Fuzz pattern generation mode
    GMODE = ""
    # If True, tests FenixEdu API
    TEST_API = False
    # Charset command line option
    CHARSET = ""
    # List of generated fuzz patterns
    GARBAGE_STRINGS = []
    # API version (only used if test_api is specified, to build the request URL)
    API_VERSION = 0
    # User role to perform login
    USER_ROLE = ""
    #
    COOKIE = ""
    #
    CONTEXT_PATH = ""

    parsed_input_values = parseInput()
    MIN_LENGTH = parsed_input_values[0]
    MAX_LENGTH = parsed_input_values[1]
    GMODE = parsed_input_values[2]
    TEST_API = parsed_input_values[3]
    CHARSET = parsed_input_values[4]
    API_VERSION = parsed_input_values[5]
    USER_ROLE = parsed_input_values[6]

    GARBAGE_STRINGS = generateFuzzPatterns(CHARSET, MIN_LENGTH, MAX_LENGTH)

    if TEST_API:
        fuzzFenixeduAPI(GARBAGE_STRINGS, API_VERSION)

    # fuzzFenixedu(GARBAGE_STRINGS, USER_ROLE)

    printFinalResults()


# Standard Python 'main' function invocation
if __name__ == '__main__':
    _main()

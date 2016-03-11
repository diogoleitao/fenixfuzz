import string
import random
import requests
import sys
import re
from bs4 import BeautifulSoup


# Prettier exit function
def quit(code):
    sys.exit(code)


# Returns a string with a given length containing a set of characters
def generate_strings(mode, length):
    all_charsets = {
        # Characters, numbers, symbols and whitespaces
        "all": string.printable,

        # Characters, numbers, symbols
        "no-white": string.letters + string.digits + string.punctuation,

        # Characters and numbers
        "alpha": string.letters + string.digits,

        # Characters
        "char": string.letters,

        # Numbers
        "num": string.digits
    }

    charset = all_charsets[mode]
    if charset is None:
        charset = string.letters + string.digits
    return ''.join(random.choice(charset) for i in range(length))


# Generates fuzz patterns with length ranging from min_length to max_length
def generate_fuzz_patterns(mode, minimum, maximum):
    strings = []
    for i in range(minimum, maximum + 1):
        strings.append(generate_strings(mode, i))
    return strings


# Parses command line arguments to:
#   - set fuzz pattern minimum and maximum length
#   - set fuzz pattern generation mode
#   - check if FenixEdu API is to also be tested
#   - retrieve API version
#   - set the charset to be used for the fuzz pattern generation
#   - choose the type of user to access FenixEdu: student, teacher or system administrator
# If any errors occur, it prints them and exits the main program
def parse_input(minimum, maximum, mode, api, charset, version, user):
    final_warning = ""

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
                    final_warning += "\n\t-min should be greater than or equal to zero."
            except ValueError:
                final_warning += "\n\t-min should be an integer."
        else:
            minimum = 1

        if "-max" in sys.argv:
            max_index = sys.argv.index("-max") + 1
            try:
                maximum = int(sys.argv[max_index])
                if maximum < 1:
                    final_warning += "\n\t-max should be greater than zero."
                elif maximum < minimum:
                    final_warning += "\n\t-max should be greater than -min."
            except ValueError:
                final_warning += "\n\t-max should be an integer."
        else:
            minimum = 20

        if "-gmode" in sys.argv:
            gmode_index = sys.argv.index("-gmode") + 1
            mode = sys.argv[gmode_index]
            if mode == "generation" or mode == "mutation":
                pass
            else:
                final_warning += "\n\t-gmode should be either generation or mutation."
        else:
            mode = "generation"

        if "-api" in sys.argv:
            api = True
            if "-v" in sys.argv:
                api_version_index = sys.argv.index("-v") + 1
                try:
                    version = int(sys.argv[api_version_index])
                except ValueError:
                    final_warning += "\n\t-v should be an integer."
            else:
                version = 1

        if "-c" in sys.argv:
            charset_index = sys.argv.index("-c") + 1
            charset = sys.argv[charset_index]
            if charset == "all" or charset == "no-white" or charset == "alpha" or charset == "char" or charset == "num":
                pass
            else:
                final_warning += "\n\t-c should be either all, no-white, alpha, char or num."
        else:
            charset = "alpha"

        if "-u" in sys.argv:
            user_index = sys.argv.index("-u") + 1
            user = sys.argv[user_index]
            if user == "student" or user == "teacher" or user == "sysadm":
                pass
            else:
                final_warning += "\n\t-u should be either student, teacher or sysadm."

        if len(final_warning) > 0:
            final_warning = "Error(s):" + final_warning
            print final_warning
            quit(1)
        else:
            return minimum, maximum, mode, api, charset, version, user


# Fuzzes the FenixEdu API and prints the sent requests
def fuzz_fenixedu_api(fuzz_patterns, version):
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
        if "{id}" not in endpoint:
            pass
            # http_request = requests.get(base_url + endpoint)
            # print str(http_request.status_code) + " " + endpoint
        else:
            for fuzz_pattern in fuzz_patterns:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.get(base_url + final_endpoint)
                if server_error_pattern.match(str(http_request.status_code)):
                    print str(http_request.status_code) + " " + final_endpoint

    for endpoint in put_endpoints:
        if "{id}" not in endpoint:
            pass
            # http_request = requests.put(base_url + endpoint)
            # print str(http_request.status_code) + " " + endpoint
        else:
            for fuzz_pattern in fuzz_patterns:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.put(base_url + final_endpoint)
                if server_error_pattern.match(str(http_request.status_code)):
                    print str(http_request.status_code) + " " + final_endpoint


# Fuzzes the FenixEdu pages
def fuzz_fenixedu(fuzz_patterns):
    fenixEdu_starfleet = "localhost:8080/starfleet/login"

    # THIS IS NOT RIGHT!
    current_page = fenixEdu_starfleet

    # LOGIN PROCESS STILL MISSING
    # do_login()

    # LINKS CRAWLER
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
        all of them are assigned a given value, but it does not reflect
        the actual final value (that is, the value assigned when the
        script is running). This is avoided with the parse_input()
        function (see its documentation).
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
    charset_mode = ""
    # List of generated fuzz patterns to be fed
    garbage_strings = []
    # API version (used to build the request URL; only needed if test_api is specified)
    api_version = 0
    # User role to perform login
    user_role = ""

    variables_tuple = parse_input(min_length, max_length, gmode, test_api, charset_mode, api_version, user_role)

    min_length = variables_tuple[0]
    max_length = variables_tuple[1]
    gmode = variables_tuple[2]
    test_api = variables_tuple[3]
    charset_mode = variables_tuple[4]
    api_version = variables_tuple[5]
    user_role = variables_tuple[6]

    # print min_length
    # print max_length
    # print gmode
    # print test_api
    # print charset_mode
    # print api_version
    # print user_role

    garbage_strings = generate_fuzz_patterns(charset_mode, min_length, max_length)

    if test_api:
        fuzz_fenixedu_api(garbage_strings, api_version)

    # fuzz_fenixedu(garbage_strings)

# Standard Python invocation
if __name__ == '__main__':
    _main()

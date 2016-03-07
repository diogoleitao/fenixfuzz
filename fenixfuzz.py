import string
import random
import requests
import sys
from bs4 import BeautifulSoup

# Minimum string length
min_length = 1
# Maximum string length
max_length = 20
# Fuzz pattern generation mode
gmode = "generation"
# If True, tests FenixEdu API
test_api = False
# Charset command line option
charset_mode = "alpha"
# List of generated fuzz patterns to be fed
garbage_strings = []
# API version (to build the request URL; only needed if test_api is specified)
api_version = 1
# FenixEdu URL (with starfleet dump)
fenixEdu_starfleet = "localhost:8080/starfleet/login"
# FenixEdu API URL
fenixEdu_URL_api = "http://fenixedu.org/dev/api/index.html"


# Returns a string with a given length containing a set of characters
def generate_strings(length):
    if charset_mode == "all":
        # Characters, numbers, symbols and whitespaces
        charset = string.printable
    elif charset_mode == "no-white":
        # Characters, numbers, symbols
        charset = string.letters + string.digits + string.punctuation
    elif charset_mode == "alpha":
        # Characters and numbers
        charset = string.letters + string.digits
    elif charset_mode == "char":
        # Characters
        charset = string.letters
    elif charset_mode == "dig":
        # Numbers
        charset = string.digits
    else:
        charset = string.letters + string.digits
    return ''.join(random.choice(charset) for i in range(length))


# Generates fuzz patterns with length ranging from min_length to max_length
def generate_fuzz_patterns():
    for i in range(min_length, max_length + 1):
        garbage_strings.append(generate_strings(i))


# Parses input arguments to:
#   - set fuzz pattern minimum and maximum length
#   - set fuzz pattern generation mode
#   - check if FenixEdu API is to also be tested
#   - retrieve API version
#   - set the charset to be used for the fuzz pattern generation
# If any errors occur, it prints them and exits the main program
def parse_input():
    final_warning = ""

    if len(sys.argv) < 2:
        print "Usage:\n\tfenixfuzz.py [-min minimum|-max maximum|-gmode generation_mode|-api|-v version|-c charset]"
        print "Options:"
        print "\t-min:\tminimum fuzz pattern length.\n\t\tAccepted values: positive integers.\n\t\tDefault value: 1.\n"
        print "\t-max:\tmaximum fuzz pattern length.\n\t\tAccepted values: integers (greater than 0).\n\t\tDefault value: 20.\n"
        print "\t-gmode:\tfuzz pattern generation mode.\n\t\tAccepted values: \"generation\" and \"mutation\".\n\t\tDefault value: generation.\n"
        print "\t-api:\tif specified, the fuzzer also tests the FenixEdu API.\n"
        print "\t-v:\tspecifies the API version.\n\t\tAccepted values: integers (greater than 0).\n\t\tDefault value: 1.\n"
        print "\t-c:\tcharset used for the fuzz patterns (a combination of letters, digits, punctuation/symbols and whitespace characters).\n\t\tAccepted values: \"all\", \"no-white\", \"alpha\", \"char\" or \"dig\".\n\t\tDefault value: \"alpha\".\n"
        sys.exit(0)
    else:
        if "-min" in sys.argv:
            min_index = sys.argv.index("-min") + 1
            try:
                min_length = int(sys.argv[min_index])
                if min_length < 0:
                    final_warning += "\n\t-min should be greater than or equal to zero."
            except ValueError:
                final_warning += "\n\t-min should be an integer."
        else:
            min_length = 1

        if "-max" in sys.argv:
            max_index = sys.argv.index("-max") + 1
            try:
                max_length = int(sys.argv[max_index])
                if max_length < 1:
                    final_warning += "\n\t-max should be greater than zero."
                elif max_length < min_length:
                    final_warning += "\n\t-max should be greater than -min."
            except ValueError:
                final_warning += "\n\t-max should be an integer."
        else:
            max_length = 20

        if "-gmode" in sys.argv:
            gmode_index = sys.argv.index("-gmode") + 1
            gmode = sys.argv[gmode_index]
            if gmode == "generation" or gmode == "mutation":
                pass
            else:
                final_warning += "\n\t-gmode should be either \"generation\" or \"mutation\"."
        else:
            gmode = "generation"

        if "-api" in sys.argv:
            test_api = True
            if "-v" in sys.argv:
                api_version_index = sys.argv.index("-v") + 1
                try:
                    api_version = int(sys.argv[api_version_index])
                except ValueError:
                    final_warning += "\n\t-v should be an integer."
            else:
                api_version = 1

        if "-c" in sys.argv:
            charset_index = sys.argv.index("-c") + 1
            charset_mode = sys.argv[charset_index]
            if charset_mode == "all" or charset_mode == "no-white" or charset_mode == "alpha" or charset_mode == "char" or charset_mode == "dig":
                pass
            else:
                final_warning += "\n\t-c should be either \"all\", \"no-white\", \"alpha\", \"char\" or \"dig\"."
        else:
            charset_mode = "alpha"

        if len(final_warning) > 0:
            final_warning = "Error(s):" + final_warning
            print final_warning
            sys.exit(1)


# Fuzzes the FenixEdu API and prints the sent requests
def fuzz_fenixedu_api():
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

    base_url = "https://fenix.tecnico.ulisboa.pt/api/fenix/v" + api_version
    for endpoint in get_endpoints:
        if "{id}" not in endpoint:
            http_request = requests.get(base_url + endpoint)
            print str(http_request.status_code) + " " + endpoint
        else:
            for fuzz_pattern in garbage_strings:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.get(base_url + final_endpoint)
                print str(http_request.status_code) + " " + final_endpoint

    for endpoint in put_endpoints:
        if "{id}" not in endpoint:
            http_request = requests.put(base_url + endpoint)
            print str(http_request.status_code) + " " + endpoint
        else:
            for fuzz_pattern in garbage_strings:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.put(base_url + final_endpoint)
                print str(http_request.status_code) + " " + final_endpoint


# Fuzzes the FenixEdu pages
def fuzz_fenixedu():
    # THIS IS NOT RIGHT!
    current_page = fenixEdu_starfleet

    # LOGIN PROCESS STILL MISSING
    # do_login()

    """
        LINKS CRAWLER
    """
    page = requests.get(current_page).text
    html_tree = BeautifulSoup(page, 'html_parser')
    all_links = html_tree.find_all('a')
    parsed_links = []
    for link in all_links:
        anchor = link.get("href")
        if "http://localhost:8080/" in anchor:
            parsed_links.append(anchor)

    """
        FORM CRAWLER
    """
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


# Main program structure
def _main():
    parse_input()
    generate_fuzz_patterns()
    # fuzz_fenixedu_api()
    fuzz_fenixedu()

# Standard Python invocation
if __name__ == '__main__':
    _main()

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


# Generates a string with a given length containing random characters and/or numbers and/or symbols
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


#
def generate_fuzz_patterns():
    for i in range(min_length, max_length + 1):
        garbage_strings.append(generate_strings(i))


# Parses input arguments to:
#   - get fuzz pattern minimum and maximum length
#   - get fuzz pattern generation mode
#   - check if FenixEdu API is to also be tested
def parse_input():
    final_warning = ""

    if len(sys.argv) < 2:
        print "Usage:\n\tfenixfuzz.py [-min value|-max value|-gmode value|-api|-c value]"
        print "Options:"
        print "\t-min:\tminimum fuzz pattern length.\n\t\tAccepted values: integers.\n\t\tDefault value: 1.\n"
        print "\t-max:\tmaximum fuzz pattern length.\n\t\tAccepted values: integers (greater than 0).\n\t\tDefault value: 20.\n"
        print "\t-gmode:\tfuzz pattern generation mode.\n\t\tAccepted values: \"generation\" and \"mutation\".\n\t\tDefault value: generation.\n"
        print "\t-api:\tif passed, tests the FenixEdu API."
        print "\t-c:\tcharset used (a combination of letters, digits, punctuation/symbols and whitespace characters).\n\t\tAccepted values: \"all\", \"no-white\", \"alpha\", \"char\" or \"dig\".\n\t\tDefault value: \"alpha\"."
        print ""
        sys.exit(0)
    else:
        if "-min" in sys.argv:
            min_index = sys.argv.index("-min") + 1
            try:
                min_length = int(sys.argv[min_index])
                if min_length < 0:
                    final_warning += "\n\t-min should be greater than zero."
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

        test_api = "-api" in sys.argv

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


#
#
def fuzz_fenixedu_api():
    get_endpoints = []
    put_endpoints = []

    fenixedu_page = requests.get("http://fenixedu.org/dev/api/index.html").text
    html_tree = BeautifulSoup(fenixedu_page, 'html.parser')
    endpoints_list = html_tree.find_all('a')
    for endpoint in endpoints_list:
        real_endpoint = endpoint.getText()
        if "GET" in real_endpoint:
            get_endpoints.append(real_endpoint[4:])
        elif "PUT" in real_endpoint:
            put_endpoints.append(real_endpoint[4:])

    for endpoint in get_endpoints:
        if "{id}" not in endpoint:
            http_request = requests.get(endpoint)
            print str(http_request.status_code) + " " + endpoint
        else:
            for fuzz_pattern in garbage_strings:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.get(final_endpoint)
                print str(http_request.status_code) + " " + final_endpoint

    for endpoint in put_endpoints:
        if "{id}" not in endpoint:
            http_request = requests.put(endpoint)
            print str(http_request.status_code) + " " + endpoint
        else:
            for fuzz_pattern in garbage_strings:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.put(final_endpoint)
                print str(http_request.status_code) + " " + final_endpoint


def fuzz_fenixedu():
    # TODO
    return


#
#
def _main():
    parse_input()
    print min_length
    print max_length
    print gmode
    print test_api
    print charset_mode
    generate_fuzz_patterns()
    # fuzz_fenixedu_api()
    fuzz_fenixedu()

#
#
if __name__ == '__main__':
    _main()

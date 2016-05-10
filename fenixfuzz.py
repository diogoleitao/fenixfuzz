"""Sample docstring"""
import random
import re
import requests
import string
import sys

from bs4 import BeautifulSoup

import globalvars
from scraping import LinkCrawler, FormParser


def generate_strings(charset, length):
    """
        Returns a string with a given length containing a subset of
        characters from a given charset.
    """

    return ''.join(random.choice(charset) for i in range(length))


def generate_fuzz_patterns(mode, minimum, maximum):
    """
        Returns an array of fuzz pattern strings with variable lengths,
        ranging from min_length to max_length. Each string is made up of a
        subset of characters, based on the charset given as input.
    """

    if mode == "generation":
        fuzz_patterns = []
        for i in range(minimum, maximum + 1):
            fuzz_patterns.append(generate_strings(globalvars.CHARSET, i))
        globalvars.GARBAGE_STRINGS = fuzz_patterns
    elif mode == "mutation":
        known_bad = []
        with open("bad_input", "r") as bad_input_file:
            known_bad.append(bad_input_file.readline)
        # DO MUTATION ON ACQUIRED STRING


# Needs to be determined in what way it is presented and what information is
# important to be shown to the fenixedu developers
def dump_results():
    """
        Sample docstring
    """
    return


def parse_input():
    """
        Parses command line arguments to:
            - set fuzz pattern's minimum and maximum length;
            - set fuzz pattern's generation mode;
            - check if FenixEdu API is to be tested as well;
            - retrieve API version (for when the API is being tested);
            - set the charset used for the fuzz pattern generation;
            - choose the type of user to access FenixEdu: student, teacher or
            system administrator;
        Some arguments have default values; so, if they're not specified,
        each option will fall back to its default value. Note however that
        some options must be specified, and thus, don't have default values.
        If any errors occur, they are printed out and the main program exits
        with error code 1.
    """

    defaults_warning = "Option {0} was not specified; using default value: {1}"

    minimum = 1
    maximum = 20
    mode = "generation"
    api = False
    charset = string.letters + string.digits
    version = 1
    user = "student"
    errors = ""

    if "-h" in sys.argv or "--help" in sys.argv:
        print("Usage:\tfenixfuzz.py [OPTIONS]")
        print("Some options don't have a default value and must be specified, or else the script won't run.\n")
        print("Options:")
        print("-m, --minimum:\tminimum fuzz pattern length.\n\
                Accepted values: positive integers.\n\
                Default value: 1.\n")
        print("-M, --maximum:\tmaximum fuzz pattern length.\n\
                Accepted values: positive integers.\n\
                Default value: 20.\n")
        print("-g, --genmode:\tfuzz pattern generation mode.\n\
                Accepted values: generation, mutation.\n\
                Default value: generation.\n")
        print("-api:\t\tif specified, the fuzzer also tests the FenixEdu API.\n")
        print("-v, --version:\tspecifies the API version.\n\
                Accepted values: positive integers.\n\
                Default value: 1.\n")
        print("-c, --charset:\tcharset used for the fuzz patterns.\n\
                Accepted values: all, no-white, alpha, char, num.\n\
                Default value: none.\n")
        print("-u, --user:\tuser role used for the login process.\n\
                Accepted values: student, teacher or system administrator.\n\
                Default value: none.\n")
        print("-h, --help:\tshows this text.")
        sys.exit(0)
    else:
        if "-m" in sys.argv or "--minimum" in sys.argv:
            try:
                min_index = sys.argv.index("-m") + 1
            except ValueError:
                min_index = sys.argv.index("--minimum") + 1
            try:
                minimum = int(sys.argv[min_index])
                if minimum < 0:
                    errors += "\n\t- Minimum length should be greater than or equal to zero."
            except ValueError:
                errors += "\n\t- Minimum length should be an integer."
        else:
            print(defaults_warning.format("-m", str(minimum)))

        if "-M" in sys.argv or "--maximum" in sys.argv:
            try:
                max_index = sys.argv.index("-M") + 1
            except ValueError:
                max_index = sys.argv.index("--maximum") + 1
            try:
                maximum = int(sys.argv[max_index])
                if maximum < 1:
                    errors += "\n\t- Maximum length should be greater than zero."
                elif maximum < minimum:
                    errors += "\n\t- Maximum length should be greater than -min."
            except ValueError:
                errors += "\n\t- Maximum length should be an integer."
        else:
            print(defaults_warning.format("-M", str(maximum)))

        if "-g" in sys.argv or "--genmode" in sys.argv:
            try:
                gmode_index = sys.argv.index("-g") + 1
            except ValueError:
                gmode_index = sys.argv.index("--generation") + 1
            mode = sys.argv[gmode_index]
            if mode == "generation" or mode == "mutation":
                pass
            else:
                errors += "\n\t- Generation mode should be generation or mutation."
        else:
            print(defaults_warning.format("-g", mode))

        if "-api" in sys.argv:
            api = True
            if "-v" in sys.argv or "--version" in sys.argv:
                try:
                    api_version_index = sys.argv.index("-v") + 1
                except ValueError:
                    api_version_index = sys.argv.index("--version") + 1
                try:
                    version = int(sys.argv[api_version_index])
                except ValueError:
                    errors += "\n\t-Version should be an integer."
            else:
                print(defaults_warning.format("-v", str(version)))
        else:
            print(defaults_warning.format("-api", str(api)))

        if "-c" in sys.argv or "--charset" in sys.argv:
            try:
                charset_index = sys.argv.index("-c") + 1
            except ValueError:
                charset_index = sys.argv.index("--charset") + 1
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
                errors += "\n\t- Charset should be all, no-white, alpha, char or num."
        else:
            errors += "\n\t- Charset must be specified (all, no-white, alpha, char, num)."

        if "-u" in sys.argv or "--user" in sys.argv:
            try:
                user_index = sys.argv.index("-u") + 1
            except ValueError:
                user_index = sys.argv.index("--user") + 1
            user = sys.argv[user_index]
            teacher = str(random.randrange(2, 15, 1))
            student = str(random.randrange(16, 30, 1))
            all_users = {
                'sysadm': 'SA1',
                'teacher': 'SA' + teacher,
                'student': 'SA' + student
            }
            try:
                user = all_users[user]
            except KeyError:
                errors += "\n\t- User should be student, teacher or sysadm."
        else:
            errors += "\n\t- User must be specified (student, teacher, sysadm)."

        if len(errors) > 0:
            print("Error(s):" + errors)
            sys.exit(1)
        else:
            globalvars.MIN_LENGTH = minimum
            globalvars.MAX_LENGTH = maximum
            globalvars.GMODE = mode
            globalvars.TEST_API = api
            globalvars.CHARSET = charset
            globalvars.API_VERSION = str(version)
            globalvars.USER_ROLE = user


def fuzz_fenixedu_api(version, fuzz_patterns):
    """
        Fuzzes the FenixEdu API and prints the requests sent which triggered
        a server side error. The API endpoints are retrieved via its
        documentation webpage, by parsing the bullet list and retrieving only
        the endpoint (e.g.: /courses/{id}). The final URL used for the
        request is built using th base url, concatenated with the current
        endpoint being tested and with the current fuzz pattern.
    """

    fenixedu_api_url = "http://fenixedu.org/dev/api/index.html"
    get_endpoints = []
    put_endpoints = []

    fenixedu_page = requests.get(fenixedu_api_url).text
    html_tree = BeautifulSoup(fenixedu_page, 'html.parser')
    endpoints_list = html_tree.find_all('a')
    for endpoint in endpoints_list:
        slug = endpoint.getText()
        if slug.startswith("GET"):
            get_endpoints.append(slug[4:])
        elif slug.startswith("PUT"):
            put_endpoints.append(slug[4:])

    base_url = "https://fenix.tecnico.ulisboa.pt/api/fenix/v" + version
    server_error_pattern = re.compile("^5[0-9][0-9]$")

    for endpoint in get_endpoints:
        if "{id}" in endpoint:
            for fuzz_pattern in fuzz_patterns:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.get(base_url + final_endpoint)
                if server_error_pattern.match(str(http_request.status_code)):
                    print(str(http_request.status_code) + " " + final_endpoint)

    for endpoint in put_endpoints:
        if "{id}" in endpoint:
            for fuzz_pattern in fuzz_patterns:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.put(base_url + final_endpoint)
                if server_error_pattern.match(str(http_request.status_code)):
                    print(str(http_request.status_code) + " " + final_endpoint)


def login(role):
    """
        Performs login at the local Fenix instance and sets the globalvars.py
        cookie dictionary needed for each request.
    """

    login_url = "http://localhost:8080/starfleet/api/bennu-core/profile/login"
    username_password = {'username': role, 'password': ''}
    response = requests.post(login_url, data=username_password)
    cookies = response.headers.get('set-cookie').replace(';', '').replace(',', '').split(' ')
    context_path = cookies[0].split('=')[1]
    jsessionid = cookies[2].split('=')[1]

    globalvars.COOKIES = {
        'JSESSIONID': jsessionid,
        'contextPath': context_path
    }


def fuzz_fenixedu(role):
    """
        ...
        It also populates a queue with links from the 'home' page, which are
        used to crawl the whole website.

        base_url = globalvars.BASE_URL + globalvars.COOKIES['contextPath']
        page_url = base_url + "/home.do"
        landing_page = requests.post(page_url, cookies=globalvars.COOKIES).text
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
    """

    login(role)

    home_url = globalvars.BASE_URL + "/starfleet/home.do"
    crawler_populate = LinkCrawler(home_url, globalvars.COOKIES)
    crawler_populate.crawl()

    while globalvars.LINKS_QUEUE:
        url = globalvars.LINKS_QUEUE.popleft()
        link_crawler = LinkCrawler(url, globalvars.COOKIES)
        link_crawler.crawl()

    while globalvars.CRAWLED_LINKS_QUEUE:
        url = globalvars.CRAWLED_LINKS_QUEUE.popleft()
        form_parser = FormParser(url, globalvars.COOKIES)
        form_parser.parse()


def _main():
    """
        Main program flow
    """

    parse_input()

    generate_fuzz_patterns(globalvars.GMODE, globalvars.MIN_LENGTH, globalvars.MAX_LENGTH)

    if globalvars.TEST_API:
        fuzz_fenixedu_api(globalvars.API_VERSION, globalvars.GARBAGE_STRINGS)

    # fuzz_fenixedu(globalvars.USER_ROLE)

    dump_results()

if __name__ == '__main__':
    _main()

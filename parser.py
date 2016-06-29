import sys
from urllib.parse import urlparse
import requests

import globalvars
from scraping import FormParser, LinkCrawler
from utils import terminate, read_properties_file


# The help message to be displayed. It is "oddly" formatted so it is easier to
# see how the final product will look (instead of using \t and \n characters
# to align everything).
HELP_MESSAGE = "\
USAGE:\n\
        parser.py [OPTIONS]\n\n\
OPTIONS:\n\
-f, --file:\n\
        Path to the .properties file needed to configure the fuzzer.\n\
        Example: '/path/to/fenixfuzz.properties'.\n\n\
-h, --help:\n\
        Shows this text."


def _main():
    """
        The FenixFuzz main flow
    """

    if "-h" in sys.argv or "--help" in sys.argv:
        terminate(HELP_MESSAGE, 0)
    elif "-f" in sys.argv or "--file" in sys.argv:
        try:
            path_index = sys.argv.index("-f") + 1
        except ValueError:
            path_index = sys.argv.index("--file") + 1
        try:
            path = sys.argv[path_index]
        except IndexError:
            terminate("Please check that a value was specified for the -f/--file option.", 1)
    else:
        terminate("-f/--file option not specified", 1)

    properties = read_properties_file(path)

    globalvars.MINIMUM = properties["minimum"]
    globalvars.MAXIMUM = properties["maximum"]
    globalvars.GENMODE = properties["genmode"]
    globalvars.TEST_API = properties["test_api"]
    globalvars.API_VERSION = properties["api_version"]
    globalvars.CHARSET = properties["charset"]
    globalvars.USER = properties["user"]
    globalvars.EXCLUDE_URLS_FILE = properties["exclude_urls"]
    globalvars.FENIXFUZZ_MODEL_FILE = properties["fenixfuzz_model"]

    path_array = urlparse(properties["local_instance"])
    protocol = path_array.scheme
    host = path_array.netloc

    globalvars.BASE_URL = protocol + '://' + host
    if path_array.path.endswith("/"):
        path_array = path_array[:-1]
    globalvars.LOCAL_CONTEXT_PATH = path_array.path

    login_url = globalvars.BASE_URL + globalvars.LOCAL_CONTEXT_PATH + "/api/bennu-core/profile/login"
    login_data = {
        "username": globalvars.USER,
        "password": ""
    }

    response = requests.post(login_url, data=login_data)
    cookies = response.headers.get("set-cookie")
    cookies = cookies.replace(";", "").replace(",", "").split(" ")

    context_path = cookies[0].split("=")[1]
    jsessionid = cookies[2].split("=")[1]

    globalvars.COOKIES = {
        "JSESSIONID": jsessionid,
        "contextPath": context_path
    }

    home_url = globalvars.BASE_URL + globalvars.LOCAL_CONTEXT_PATH + "/home.do"
    globalvars.LINKS_QUEUE.append(home_url)

    populate = LinkCrawler(globalvars.LINKS_QUEUE.popleft(), globalvars.COOKIES)
    populate.crawl()

    while globalvars.LINKS_QUEUE:
        url = globalvars.LINKS_QUEUE.popleft()
        link_crawler = LinkCrawler(url, globalvars.COOKIES)
        link_crawler.crawl()

    if 1 == 1:
        return

    while globalvars.CRAWLED_LINKS_QUEUE:
        url = globalvars.CRAWLED_LINKS_QUEUE.popleft()
        form_parser = FormParser(url, globalvars.COOKIES)
        form_parser.parse()


# Standard Python "main" invocation
if __name__ == "__main__":
    _main()

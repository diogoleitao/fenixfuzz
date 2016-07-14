import sys
from urllib.parse import urlparse
import threading
import requests

import globalvars
from scraping import FormParser, LinkCrawler
from utils import terminate, read_properties_file


# The help message to be displayed. It is "oddly" formatted so it is easier to
# see how the final product will look (instead of using \t and \n characters
# to align everything).
HELP_TEXT = "\
USAGE:\n\
        parser.py -f [FILE] [OPTIONS]\n\n\
OPTIONS:\n\
-f, --file:\n\
        Path to the .properties file needed to configure the fuzzer.\n\
        Example: /path/to/fenixfuzz.properties.\n\n\
-l, --url:\n\
        Override starting URL. Useful when one wants to test a specific page and that page only.\n\
        Example: /page.do.\n\n\
-i, --iter:\n\
        How many times the tool will fuzz Fenix, by reusing the inputs with the best results.\n\
        Defaults to 1 if not specified.\n\
        Example: 2.\n\n\
-h, --help:\n\
        Shows this text."

HELP_MESSAGE = "Please check that a value was correctly specified for the {0} option."


def _main():
    """
        The FenixFuzz main flow
    """

    if "-h" in sys.argv or "--help" in sys.argv:
        terminate(HELP_TEXT, 0)
    elif "-l" in sys.argv or "--url" in sys.argv:
        try:
            url_index = sys.argv.index("-l") + 1
        except ValueError:
            url_index = sys.argv.index("--url") + 1
        try:
            globalvars.START_PAGE = sys.argv[url_index]
        except IndexError:
            terminate(HELP_MESSAGE.format("-l/--url"), 1)
    elif "-i" in sys.argv or "--iter" in sys.argv:
        try:
            iter_index = sys.argv.index("-i") + 1
        except ValueError:
            iter_index = sys.argv.index("--iter") + 1
        try:
            globalvars.ITERATIONS = sys.argv[iter_index]
        except IndexError:
            terminate(HELP_MESSAGE.format("-i/--iter"), 1)
    elif "-f" in sys.argv or "--file" in sys.argv:
        try:
            path_index = sys.argv.index("-f") + 1
        except ValueError:
            path_index = sys.argv.index("--file") + 1
        try:
            path = sys.argv[path_index]
        except IndexError:
            terminate(HELP_MESSAGE.format("-f/--file"), 1)
    else:
        terminate("-f/--file option not specified", 1)

    properties = read_properties_file(path)

    globalvars.MINIMUM = properties["minimum"]
    globalvars.MAXIMUM = properties["maximum"]
    globalvars.TEST_API = properties["test_api"]
    globalvars.API_VERSION = properties["api_version"]
    globalvars.CHARSET = properties["charset"]
    globalvars.USER = properties["user"]
    globalvars.EXCLUDE_URLS_FILE = properties["exclude_urls"]
    globalvars.FENIXFUZZ_MODEL_FILE = properties["fenixfuzz_model"]

    path_array = urlparse(properties["local_instance"])

    globalvars.BASE_URL = path_array.scheme + '://' + path_array.netloc
    if path_array.path.endswith("/"):
        path_array = path_array[:-1]
    globalvars.LOCAL_CONTEXT_PATH = path_array.path

    if globalvars.START_PAGE is None:
        globalvars.START_PAGE = properties["login_page"]

    globalvars.LOGIN_ENDPOINT = properties["login_endpoint"]

    login_url = globalvars.BASE_URL + globalvars.LOCAL_CONTEXT_PATH + globalvars.LOGIN_ENDPOINT
    login_data = {
        "username": globalvars.USER,
        "password": ""
    }

    response = requests.post(login_url, data=login_data)
    cookies = response.headers.get("set-cookie")
    cookies = cookies.replace(";", "").replace(",", "").split(" ")

    globalvars.COOKIES = {
        "JSESSIONID": cookies[0].split("=")[1],
        "contextPath": cookies[2].split("=")[1]
    }

    populate = LinkCrawler(globalvars.BASE_URL + globalvars.LOCAL_CONTEXT_PATH + globalvars.START_PAGE, globalvars.COOKIES)
    populate.crawl()

    crawler_threads = []
    for i in range(globalvars.CRAWLER_THREADS):
        url = globalvars.LINKS_QUEUE.get()
        link_crawler = LinkCrawler(url, globalvars.COOKIES)
        crawler_thread = threading.Thread(target=link_crawler.crawl)
        crawler_threads.append(crawler_thread)
        crawler_thread.start()

    for thread in crawler_threads:
        thread.join()

    for i in range(len(globalvars.CRAWLED_LINKS_QUEUE)):
        url = globalvars.CRAWLED_LINKS_QUEUE.popleft()
        form_parser = FormParser(url, globalvars.COOKIES)
        form_parser.parse()


# Standard Python "main" invocation
if __name__ == "__main__":
    _main()


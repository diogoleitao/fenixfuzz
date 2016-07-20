"""
    Main script
"""
from threading import Thread
from urllib.parse import urlparse
import requests

import globalvars
from scraping import FormParser
from scraping import LinkCrawler
from utils import parse_command_line
from utils import read_properties_file


def _main():
    """
        The FenixFuzz main flow:
        1. Read .properties file;
        2. Extract the context path and local instance base url;
        3. Get the start page and add it to the LINKS_QUEUE;
        4. Perform login and retrieve cookies;
        5. Crawl FenixEdu and save all the links (no duplicates);
        6. Parse every form found, fill it with fuzz patters and submit it;
        7. Dump the information gathered.
    """

    path = parse_command_line()
    properties = read_properties_file(path)

    globalvars.MINIMUM = properties["minimum"]
    globalvars.MAXIMUM = properties["maximum"]
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
        globalvars.START_PAGE = properties["start_page"]

    if not globalvars.START_PAGE.startswith(globalvars.LOCAL_CONTEXT_PATH):
        globalvars.START_PAGE = globalvars.LOCAL_CONTEXT_PATH + globalvars.START_PAGE

    globalvars.LINKS_QUEUE.put(globalvars.START_PAGE)

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
        "contextPath": cookies[0].split("=")[1],
        "JSESSIONID": cookies[2].split("=")[1]
    }

    for _ in range(globalvars.CRAWLER_THREADS):
        link_crawler = LinkCrawler(globalvars.COOKIES)
        crawler_thread = Thread(target=link_crawler.crawl)
        crawler_thread.setDaemon(True)
        crawler_thread.start()
    globalvars.LINKS_QUEUE.join()

    if 1 == 1:
        return

    for _ in range(globalvars.CRAWLER_THREADS):
        url = globalvars.CRAWLED_LINKS_QUEUE.popleft()
        form_parser = FormParser(url, globalvars.COOKIES)
        form_parser.parse()


# Standard Python "main" invocation
if __name__ == "__main__":
    _main()

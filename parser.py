"""
    Main script
"""

from urllib.parse import urlparse
import threading
import requests

import globalvars
from scraping import FormParser, LinkCrawler
from utils import read_properties_file, parse_command_line


def _main():
    """
        The FenixFuzz main flow
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

    globalvars.LOGIN_ENDPOINT = properties["login_endpoint"]

    login_url = globalvars.BASE_URL + globalvars.LOCAL_CONTEXT_PATH + globalvars.LOGIN_ENDPOINT
    login_data = {
        "username": globalvars.USER,
        "password": ""
    }

    if 1 == 1:
        return

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

    print(globalvars.CRAWLED_LINKS_QUEUE)

    for i in range(len(globalvars.CRAWLED_LINKS_QUEUE)):
        url = globalvars.CRAWLED_LINKS_QUEUE.popleft()
        form_parser = FormParser(url, globalvars.COOKIES)
        form_parser.parse()


# Standard Python "main" invocation
if __name__ == "__main__":
    _main()

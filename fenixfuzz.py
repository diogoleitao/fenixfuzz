"""
    Main script
"""

from urllib.parse import urlparse
import requests

import globalvars
from report import generate_html_report
from scraping import FormParser
from scraping import LinkCrawler
from utils import parse_command_line
from utils import read_exclude_urls_file
from utils import read_properties_file


def main():
    """
        The FenixFuzz main flow:
        1. Read fenixfuzz.properties file;
        2. Extract the context path and local instance base url;
        3. Get the start page and add it to the LINKS_QUEUE;
        4. Perform login and retrieve cookies;
        5. Crawl FenixEdu and save all the links (no duplicates);
        6. Parse every form found, fill it with the input generated, submit it
           and register the outcome;
        7. Generate the report files with the information gathered.
    """

    path = parse_command_line()
    properties = read_properties_file(path)

    globalvars.MINIMUM = properties["minimum"]
    globalvars.MAXIMUM = properties["maximum"]
    globalvars.CHARSET = properties["charset"]
    globalvars.USER = properties["user"]

    globalvars.EXCLUDE_URLS_FILE = properties["exclude_urls"]
    read_exclude_urls_file()

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
    globalvars.LINKS_QUEUE.append(globalvars.START_PAGE)

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

    while globalvars.LINKS_QUEUE:
        url = globalvars.LINKS_QUEUE.popleft()
        link_crawler = LinkCrawler(url, globalvars.COOKIES)
        link_crawler.run()

    while globalvars.CRAWLED_LINKS_QUEUE:
        url = globalvars.CRAWLED_LINKS_QUEUE.popleft()
        form_parser = FormParser(url, globalvars.COOKIES)
        form_parser.run()

    if 1 == 1:
        return

    generate_html_report()

# Standard Python "main" invocation
if __name__ == "__main__":
    main()

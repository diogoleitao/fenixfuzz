"""
    Main script
"""

from urllib.parse import urlparse
import requests

import globalvars
import grammar
import report
import scraping
import utils
import submitter


def bootstrap():
    """
        Read all the files and load all definitions needed to start fuzzing
    """

    globalvars.JSON_FILE_PATH, globalvars.REPORT_FILE_PATH, globalvars.HTML_REPORT, ffm_path = utils.parse_command_line()
    properties = utils.read_properties_file(ffm_path)

    globalvars.MINIMUM = properties["minimum"]
    globalvars.MAXIMUM = properties["maximum"]
    globalvars.CHARSET = properties["charset"]
    globalvars.USER = properties["user"]

    exclude_urls, sample_urls = utils.read_url_patterns_file(properties["url_patterns"])
    scraping.EXCLUDE_URLS += exclude_urls
    scraping.SAMPLE_URLS += sample_urls

    grammar.GRAMMAR = utils.read_fenixfuzz_model_file(properties["fenixfuzz_model"])

    url_array = urlparse(properties["local_instance"])
    globalvars.BASE_URL = url_array.scheme + '://' + url_array.netloc
    if url_array.path.endswith("/"):
        url_array = url_array[:-1]
    globalvars.CONTEXT_PATH = url_array.path

    if not globalvars.START_PAGE.startswith(globalvars.CONTEXT_PATH):
        globalvars.START_PAGE = globalvars.CONTEXT_PATH + globalvars.START_PAGE
    globalvars.LINKS_QUEUE.append(globalvars.START_PAGE)

    globalvars.LOGIN_ENDPOINT = properties["login_endpoint"]
    login_url = globalvars.BASE_URL + globalvars.CONTEXT_PATH + globalvars.LOGIN_ENDPOINT

    response = requests.post(login_url, data={"username": globalvars.USER, "password": ""})
    cookies = response.headers.get("set-cookie").replace(";", "").replace(",", "").split(" ")
    globalvars.COOKIES = {
        "contextPath": cookies[0].split("=")[1],
        "JSESSIONID": cookies[2].split("=")[1]
    }


def main():
    """
        The FenixFuzz main flow:
        1. Read fenixfuzz.properties file;
        2. Extract the context path and local instance base url;
        3. Get the start page and add it to the LINKS_QUEUE;
        4. Perform login and retrieve cookies;
        5. Crawl FenixEdu and save all the links (no duplicates) and forms found;
        6. Parse every form, fill it with the input generated, submit it and register the outcome;
        7. Generate the report files with the information gathered.
    """

    bootstrap()

    while globalvars.LINKS_QUEUE:
        scraping.crawl(globalvars.LINKS_QUEUE.popleft(), globalvars.COOKIES)

    while globalvars.CRAWLED_LINKS_QUEUE:
        scraping.parse(globalvars.CRAWLED_LINKS_QUEUE.popleft(), globalvars.COOKIES)

    while globalvars.PARSED_FORMS_QUEUE:
        submitter.submit(globalvars.PARSED_FORMS_QUEUE.popleft(), globalvars.COOKIES)

    report.generate_json_report()

    if globalvars.HTML_REPORT:
        report.generate_html_report()


if __name__ == "__main__":
    main()

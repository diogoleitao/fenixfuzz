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

    properties_file, globalvars.JSON_REPORT_FILE, globalvars.GENERATE_HTML_REPORT, globalvars.HTML_REPORT_FILE = utils.parse_command_line()
    properties = utils.read_properties_file(properties_file)

    globalvars.MINIMUM = properties["minimum"]
    globalvars.MAXIMUM = properties["maximum"]
    globalvars.CHARSET = properties["charset"]
    globalvars.USER = properties["user"]

    exclude_urls, sample_urls = utils.read_url_patterns_file(properties["url_patterns"])
    scraping.EXCLUDE_URLS += exclude_urls
    scraping.SAMPLE_URLS += sample_urls

    print("- Excluding URLs that contain " + str(scraping.EXCLUDE_URLS))
    print("- Sampling URLs that contain " + str(scraping.SAMPLE_URLS))

    grammar.GRAMMAR = utils.read_fenixfuzz_model_file(properties["fenixfuzz_model"])

    url_array = urlparse(properties["local_instance"])
    globalvars.BASE_URL = url_array.scheme + '://' + url_array.netloc
    if url_array.path.endswith("/"):
        url_array = url_array[:-1]
    globalvars.CONTEXT_PATH = url_array.path

    print("- Local instance is " + properties["local_instance"])

    globalvars.START_PAGE = properties["start_page"]
    if not globalvars.START_PAGE.startswith(globalvars.CONTEXT_PATH):
        globalvars.START_PAGE = globalvars.CONTEXT_PATH + globalvars.START_PAGE
    globalvars.LINKS_QUEUE.append(globalvars.START_PAGE)

    print("- Starting page is " + globalvars.START_PAGE)

    globalvars.LOGIN_ENDPOINT = properties["login_endpoint"]
    login_url = globalvars.BASE_URL + globalvars.CONTEXT_PATH + globalvars.LOGIN_ENDPOINT

    print("- Login with user " + globalvars.USER + " on URL " + login_url)

    response = requests.post(login_url, headers={'X-REQUESTED-WITH': 'XMLHttpRequest'}, data={"username": globalvars.USER, "password": ""})
    cookies = response.headers.get("set-cookie").replace(";", "").replace(",", "").split(" ")

    globalvars.COOKIES = {
        "JSESSIONID": cookies[0].split("=")[1],
        "Path": cookies[1].split("=")[1]
    }

    print("- Cookies are " + str(globalvars.COOKIES))


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
    print("Bootstraping FenixFuzz...")
    bootstrap()
    print("Finished bootstraping.")

    while globalvars.LINKS_QUEUE:
        scraping.crawl(globalvars.LINKS_QUEUE.popleft(), globalvars.COOKIES)

    print("Total unique links found:" + len(globalvars.CRAWLED_LINKS_QUEUE))
    while globalvars.CRAWLED_LINKS_QUEUE:
        scraping.parse(globalvars.CRAWLED_LINKS_QUEUE.popleft(), globalvars.COOKIES)

    print("Total forms found:" + len(globalvars.PARSED_FORMS_QUEUE))
    while globalvars.PARSED_FORMS_QUEUE:
        submitter.submit(globalvars.PARSED_FORMS_QUEUE.popleft(), globalvars.COOKIES)

    report.generate_json_report()

    if globalvars.GENERATE_HTML_REPORT:
        report.generate_html_report()


if __name__ == "__main__":
    main()

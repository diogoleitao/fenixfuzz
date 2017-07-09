"""
    FenixEdu web scraping module
"""

import string
import requests

from bs4 import BeautifulSoup

from form import Form
import globalvars
import grammar

EXCLUDE_URLS = []
SAMPLE_URLS = []


def normalize_url(url):
    """
        Normalizes the url to match the format http://<local_instance>/<context_path>/<page>
    """
    return globalvars.BASE_URL + url if url.startswith("/") else url


def excludable(url):
    """
        Checks if the url should be excluded from the crawling process. This is due to some urls
        containing weird characters that in turn cause a weird behaviour on the crawler, creating
        new links each time they're visited.
    """

    accented_chars = "ãâáàäẽêéèëĩîíìïõôóòöũûúùüçÃÂÁÀÄẼÊÉÈËĨÎÍÌÏÕÔÓÒÖŨÛÚÙÜÇ"
    printable_charset = string.ascii_letters + accented_chars + string.digits + string.punctuation

    non_printable = not all(char in printable_charset for char in url)
    exclude = any(pattern in url for pattern in EXCLUDE_URLS)

    return not(not non_printable and not exclude)


def crawl(url, cookies):
    """
        Performs a GET request for each link that is found. Each instance gets a link, crawls it and
        adds the new links to the queue. Two queues are used (stored in globalvars):
        - LINKS_QUEUE for adding links that have not yet been visited and
        - CRAWLED_LINKS_QUEUE for storing links that have already been visited.

        Crawls the page returned by the GET request, looking for all the links the page has, adding
        them to the queue if they weren't already visited.
    """

    print("GET on url " + url)

    if excludable(url):
        return

    response = requests.get(normalize_url(url), cookies=cookies)
    html_tree = response.text

    for anchor in BeautifulSoup(html_tree, "html.parser").find_all("a"):
        try:
            href = anchor.get("href")
            print("- New href " + str(href))

            # Only save same domain links
            if href is not None and href.startswith(globalvars.CONTEXT_PATH) or href.startswith(globalvars.BASE_URL):
                if href not in globalvars.CRAWLED_LINKS_QUEUE:
                    if any(pattern in url for pattern in SAMPLE_URLS):
                        continue
                    else:
                        globalvars.CRAWLED_LINKS_QUEUE.append(href)
                        globalvars.LINKS_QUEUE.append(href)

        except AttributeError:
            # Some of the href attributes are blank or aren't of
            # type 'string', which can't be coerced; so, we just
            # ignore the errors.
            continue


def parse(url, cookies):
    """
        Responsible for parsing all forms, by analysing the fields, filling
        them and submitting the form (via the Submitter class). Each instance
        gets a link, retrieves the page, finds its forms and fills the fields
        with the appropriate input (that is, the generated fuzz pattern).

        Finds all forms in the page, fills each field and submits
        the form to the proper URL.
    """

    print("Parsing forms on URL " + url)

    response = requests.get(normalize_url(url), cookies=cookies)
    html_tree = response.text

    field_list = []

    for form in BeautifulSoup(html_tree, "html.parser").find_all("form"):
        for field in form.find_all("input"):
            field_info = grammar.process_field(form, field)

            if field_info is not None:
                field_list.append(field_info)

        globalvars.PARSED_FORMS_QUEUE.append(Form(url, field_list, form.get("action"), form.get("method")))

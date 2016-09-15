"""
    FenixEdu web scraping classes
"""

import string
import requests

from bs4 import BeautifulSoup

from form import Form
import globalvars
import grammar
import submitter

EXCLUDE_URLS = []

def normalize_url(url):
    """
        Normalizes the url to the format
        http://<local_instance>/<context_path>/<page>
    """

    if url.startswith("/"):
        return globalvars.BASE_URL + url

    else:
        return url


class LinkCrawler(object):
    """
        Responsible for crawling FenixEdu, by performing a GET request for each
        link that is found. Each instance gets a link, crawls it and adds the
        new links to the queue. Two queues are used (stored in globalvars):
        - LINKS_QUEUE for adding links that have not yet been visited and
        - CRAWLED_LINKS_QUEUE for storing links that have already been visited.
    """

    def __init__(self, url, cookies):
        self.url = normalize_url(url)
        self.cookies = cookies

    def crawlable(self, url):
        """
            Checks if the url does not have non-printable characters or if it
            matches any of the exclude pattern.
        """

        lowercase_accented = "ãâáàäẽêéèëĩîíìïõôóòöũûúùüç"
        uppercase_accented = "ÃÂÁÀÄẼÊÉÈËĨÎÍÌÕÔÓÒÖŨÛÚÙÜÇ"

        printable_charset = (string.ascii_letters + lowercase_accented +
                             uppercase_accented + string.digits + string.punctuation)
        non_printable = not all(char in printable_charset for char in url)
        exclude = any(pattern in url for pattern in EXCLUDE_URLS)

        return not non_printable and not exclude

    def crawl(self):
        """
            Crawls the page returned by the GET request, looking for all the
            links the page has, adding them to the queue if they weren't
            already visited.
        """

        request = requests.get(self.url, cookies=self.cookies)
        html_tree = request.text
        anchors = BeautifulSoup(html_tree, "html.parser").find_all("a")

        for anchor in anchors:
            try:
                href = anchor.get("href")

                # Only save same domain links
                if (href.startswith(globalvars.LOCAL_CONTEXT_PATH) or
                        href.startswith(globalvars.BASE_URL)):

                    if href not in globalvars.CRAWLED_LINKS_QUEUE and self.crawlable(href):
                        globalvars.CRAWLED_LINKS_QUEUE.append(href)
                        globalvars.LINKS_QUEUE.append(href)
            except AttributeError:
                # Some of the href attributes are blank or aren't of
                # type 'string', which can't be coerced; so, we just
                # ignore the errors.
                continue


class FormParser(object):
    """
        Responsible for parsing all forms, by analysing the fields, filling
        them and submitting the form (via the Submitter class). Each instance
        gets a link, retrieves the page, finds its forms and fills the fields
        with the appropriate input (that is, the generated fuzz pattern).
    """

    def __init__(self, url, cookies):
        self.url = normalize_url(url)
        self.cookies = cookies

    def parse(self):
        """
            Finds all forms in the page processes, fills each field and submits
            the form to the proper URL.
        """

        request = requests.get(self.url, cookies=self.cookies)
        html_tree = request.text
        forms = BeautifulSoup(html_tree, "html.parser").find_all("form")

        for form in forms:
            form_id = form.get("id")
            form_action = form.get("action")
            form_method = form.get("method")
            field_list = []

            fields = form.find_all("input")
            for field in fields:
                field_info = grammar.process_field(form, field)

                if field_info is not None:
                    field_list.append(field_info)

            form_object = Form(self.url, form_id, field_list, form_action, form_method)
            submitter_obj = submitter.Submitter(self.url, self.cookies, form_object)
            submitter_obj.submit()

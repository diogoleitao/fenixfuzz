"""
    FenixEdu web scraping utility classes
"""

# import random
import string
import requests

from bs4 import BeautifulSoup

import globalvars
from submitter import Submitter
from form import Form, Field


def normalize_url(url):
    """
        Normalizes the url to the format
        http://<local_instance>/<context_path>/<page>
    """

    if url.startswith("/"):
        return globalvars.BASE_URL + url
    else:
        return url


def url_ok(url):
    """
        Checks if the url does not have non-printable characters or if it
        matches any of the exclude pattern.
    """

    printable_charset = string.printable + "ãâáàäẽêéèëĩîíìïõôóòöũûúùüçÇ"
    non_printable = not all(char in printable_charset for char in url)
    exclude = any(pattern in url for pattern in globalvars.EXCLUDE_URLS)
    return not non_printable and not exclude


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
                if href.startswith(globalvars.LOCAL_CONTEXT_PATH) or href.startswith(globalvars.BASE_URL):
                    if href not in globalvars.CRAWLED_LINKS_QUEUE and url_ok(href):
                        globalvars.CRAWLED_LINKS_QUEUE.append(href)
                        globalvars.LINKS_QUEUE.append(href)
            except AttributeError:
                # Some of the href attributes are blank or aren't of
                # type 'string', which can't be coerced; so, we just
                # ignore the errors.
                continue

    def run(self):
        """
            Executes the crawl function
        """
        self.crawl()


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
                field_info = self.process_field(form, field)
                if field_info is not None:
                    field_object = Field(field_info[0], field_info[1], field_info[2])
                    field_list.append(field_object)

            form_object = Form(form_id, field_list, form_action, form_method)
            submitter = Submitter(self.url, self.cookies, form_object)
            submitter.submit()

    def run(self):
        """
            Executes the parse function
        """
        self.parse()

    def process_field(self, form, field):
        """
            TODO
        """
        pass
        # try:
        #     field_name = field.get("name")
        #     field_type = field.get("type")
        #     field_value = field.get("value")

        #     if field_type == "hidden":
        #         return field_name, field_type, field_value
        #     elif field_type == "text":
        #         try:
        #             if field_name != "j_captcha_response":
        #                 fuzz_pattern = ""
        #                 name = field_name.split(":")
        #                 final_name = name[len(name) - 1]
        #                 if final_name == "studentNumber":
        #                     fuzz_pattern = "19"
        #                 elif final_name == "documentIdNumber":
        #                     fuzz_pattern = "0123456789"
        #                 elif final_name == "email":
        #                     fuzz_pattern = "mail@ist.utl.pt"
        #                 return field_name, field_type, fuzz_pattern
        #         except AttributeError:
        #             # Some input attributes are blank or aren't of type
        #             # 'string', which can't be coerced; so, we just ignore
        #             # the errors.
        #             pass
        #     elif field_type == "radio":
        #         radio_options = form.find_all("input", {"type": "radio"})
        #         selected = radio_options[random.randrange(len(radio_options))]
        #         return selected.get("name"), field_type, selected.get("value")
        #     elif field_type == "checkbox":
        #         checkboxes = form.find_all("input", {"type": "checkbox"})
        #         selected = checkboxes[random.randrange(len(checkboxes))]
        #         if selected.has_attr("value"):
        #             return selected.get("name"), field_type, selected.get("value")
        #         else:
        #             return selected.get("name"), field_type, "on"
        #     elif "date" in field_type:
        #         pass
        #     elif field_type == "email":
        #         return field_name, field_type, "example@example.com"
        #     elif field_type == "search":
        #         pass
        # except AttributeError:
        #     # Some input attributes are blank or aren't of type 'string', which
        #     # can't be coerced; so, we just ignore the errors.
        #     pass

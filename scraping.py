"""
    FenixEdu web scraping utility classes
"""
import string
import json
import random
import requests

from bs4 import BeautifulSoup

import globalvars
from submitter import Submitter


class LinkCrawler(object):
    """
        Responsible for crawling FenixEdu, by performing a GET request for each
        link that is found. Each instance gets a link, crawls it and adds the
        new links to the queue. Two queues are used (stored in globalvars):
        - LINKS_QUEUE for adding links that have not yet been visited and
        - CRAWLED_LINKS_QUEUE for storing links that have already been visited.
    """

    def __init__(self, url, cookies):
        self.cookies = cookies
        self.exclude_patterns = ["/downloadFile", "/logout"]

        if url.startswith("/"):
            self.url = globalvars.BASE_URL + url
        else:
            self.url = url

        with open(globalvars.EXCLUDE_URLS_FILE, "r") as exclude_patterns_file:
            self.exclude_patterns += json.loads(exclude_patterns_file.read())

    def filter_url(self):
        """
            Checks if the url has only Python's printable characters or if it
            matches a specific pattern.
        """

        has_strange_characters = not all(char in string.printable for char in self.url)
        has_pattern_occurences = any(pattern in self.url for pattern in self.exclude_patterns)

        return not has_strange_characters and not has_pattern_occurences

    def crawl(self):
        """
            Crawls the page returned by the GET request, looking for all the
            links the page has, adding to the queue if they weren't already
            visited.
        """

        filtered = self.filter_url()

        if filtered:
            request = requests.get(self.url, cookies=self.cookies)
            html_tree = request.text
            anchors = BeautifulSoup(html_tree, "html.parser").find_all("a")

            for anchor in anchors:
                try:
                    href = anchor.get("href")

                    # Only save same domain links
                    if href.startswith(globalvars.LOCAL_CONTEXT_PATH):
                        if href not in globalvars.CRAWLED_LINKS_QUEUE:
                            globalvars.CRAWLED_LINKS_QUEUE.append(href)
                            globalvars.LINKS_QUEUE.put(href)

                    elif href.startswith(globalvars.BASE_URL):
                        if href not in globalvars.CRAWLED_LINKS_QUEUE:
                            globalvars.CRAWLED_LINKS_QUEUE.append(href)
                            globalvars.LINKS_QUEUE.put(href)

                except AttributeError:
                    # Some of the href attributes are blank or aren't of type
                    # 'string', which can't be coerced; so, we just ignore
                    # the errors
                    continue

        globalvars.LINKS_QUEUE.task_done()


class FormParser(object):
    """
        Responsible for parsing all forms, by analysing the fields, filling
        them and submitting the form (via the Submitter class). Each instance
        gets a link, retrieves the page, finds its forms and fills the fields
        with the appropriate input (that is, the generated fuzz pattern).
    """

    def __init__(self, url, cookies):
        if url.startswith("/"):
            self.url = globalvars.BASE_URL + url
        else:
            self.url = url
        self.cookies = cookies

    def parse(self):
        """
            Finds all forms in the page processes and fills each field by type
            and submits the form to the proper URL (via the Submitter class)
        """

        request = requests.get(self.url, cookies=self.cookies)
        html_tree = request.text
        forms = BeautifulSoup(html_tree, "html.parser").find_all("form")

        for form in forms:
            form_data_payload = {}
            fields = form.find_all("input")

            for field in fields:
                name_value_pair = self.process_field_by_type(form, field)

                if name_value_pair is not None:
                    form_data_payload[name_value_pair[0]] = name_value_pair[1]

            submitter = Submitter(self.url, self.cookies, form.get("action"), form.get("method"), form_data_payload)
            submitter.submit()

    def process_field_by_type(self, form, field):
        """
            bla
        """

        try:
            field_type = field.get("type")
            field_name = field.get("name")
            field_value = field.get("value")

            if field_type == "hidden":
                # print(field_type + " " + field_name)
                return field_name, field_value

            elif field_type == "text":
                # print(field_type + " " + field_name)
                try:
                    if field_name != "j_captcha_response":
                        fuzz_pattern = ""

                        name = field_name.split(":")
                        final_name = name[len(name) - 1]

                        if final_name == "studentNumber":
                            fuzz_pattern = "19"
                        elif final_name == "documentIdNumber":
                            fuzz_pattern = "0123456789"
                        elif final_name == "email":
                            fuzz_pattern = "mail@ist.utl.pt"
                        return field_name, fuzz_pattern

                except AttributeError:
                    # Some input attributes are blank or aren't of type
                    # 'string', which can't be coerced; so, we just ignore
                    # the errors
                    pass

            elif field_type == "radio":
                # print(field_type + " " + field_name)
                radio_options = form.find_all("input", {"type": "radio"})
                selected = radio_options[random.randrange(len(radio_options))]

                return selected.get("name"), selected.get("value")

            elif field_type == "checkbox":
                # print(field_type + " " + field_name)
                checkboxes = form.find_all("input", {"type": "checkbox"})
                selected = checkboxes[random.randrange(len(checkboxes))]

                if selected.has_attr("value"):
                    return selected.get("name"), selected.get("value")
                else:
                    return selected.get("name"), "on"

            elif "date" in field_type:
                # print(field_type + " " + field_name)
                pass

            elif field_type == "email":
                # print(field_type + " " + field_name)
                return field_name, "example@example.com"

            elif field_type == "search":
                # print(field_type + " " + field_name)
                pass

        except AttributeError:
            # Some input attributes are blank or aren't of  type 'string',
            # which can't be coerced; so, we just ignore the errors
            pass

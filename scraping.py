"""
    FenixEdu web scraping utility classes
"""
import string
import json
import random
import requests

from bs4 import BeautifulSoup

import globalvars
from Submitter import Submitter
from FuzzGenerator import FuzzGenerator


class LinkCrawler(object):
    """
        bla
    """
    url = ""
    cookies = {}
    exclude_patterns = ["/logout", "/downloadFile"]

    def __init__(self, url, cookies):
        self.cookies = cookies

        if url.startswith("/"):
            self.url = globalvars.BASE_URL + url
        else:
            self.url = url

        with open("config/exclude.json", "r") as exclude_patterns_file:
            self.exclude_patterns = json.loads(exclude_patterns_file.read())

    def filter_url(self):
        """
            Checks if the url has only printable characters or if it contains
            a specific pattern. These patterns should be avoided, because
            the associated GET requests that may be performed have results
            that compromise the tool"s flow.
        """

        has_strange_characters = not all(char in string.printable for char in self.url)
        has_pattern_occurences = any(pattern in self.url for pattern in self.exclude_patterns)

        return not has_strange_characters and not has_pattern_occurences

    def crawl(self):
        """
            Crawls the page returned by the GET request performed on the
            instance"s url, looking for all the links the page has and adds each
            link if it"s not present in the CRAWLED_LINKS_QUEUE global variable
        """
        filtered = self.filter_url()

        if filtered:
            request = requests.get(self.url, cookies=self.cookies)
            html_tree = request.text
            anchors = BeautifulSoup(html_tree, "html.parser").find_all("a")
            for anchor in anchors:
                href = anchor.get("href")
                try:
                    # Only save same domain links
                    if href.startswith(globalvars.COOKIES["contextPath"]) or href.startswith(globalvars.BASE_URL):
                        if href not in globalvars.CRAWLED_LINKS_QUEUE:
                            # print "\t" + href
                            globalvars.CRAWLED_LINKS_QUEUE.append(href)
                            globalvars.LINKS_QUEUE.append(href)

                except AttributeError:
                    # Some of the href attributes are blank or aren"t of type
                    # "string", which can"t be coerced; so, we just ignore
                    # the errors
                    continue


class FormParser(object):
    """
        bla
    """
    url = ""
    cookies = {}

    def __init__(self, url, cookies):
        if url.startswith("/"):
            self.url = globalvars.BASE_URL + url
        else:
            self.url = url
        self.cookies = cookies

    def parse(self):
        """
            Finds all forms present in the page returned by the GET request,
            processes its fields and submits the form to the proper URL
        """

        request = requests.get(self.url, cookies=self.cookies)
        html_tree = request.text
        forms = BeautifulSoup(html_tree, "html.parser").find_all("form")
        for form in forms:
            fields = form.find_all("input")
            for field in fields:
                form_data_payload = self.process_by_field_type(form, field)

            submitter = Submitter(self.url, self.cookies, form.get("action"), form_data_payload)
            submitter.submit()
            input()

    def process_by_field_type(self, form, field):
        """
            bla
        """

        form_data_payload = {}
        try:
            field_type = field.get("type")

            if field_type == "hidden":
                form_data_payload[field.get("name")] = field.get("value")

            elif field_type == "text":
                try:
                    if field.get("name") != "j_captcha_response":
                        fuzz_generator = FuzzGenerator()
                        fuzz_pattern = fuzz_generator.generate(field_type, field.get("max"), field.get("min"))

                        # print("Name " + field.get("name"))
                        # print("Fuzz " + fuzz_pattern)

                        form_data_payload[field.get("name")] = fuzz_pattern

                except AttributeError:
                    # Some input attributes are blank or aren"t of type
                    # "string", which can"t be coerced; so, we just ignore
                    # the errors
                    pass

            elif field_type == "radio":
                radio_options = form.get("input", {"type": "radio"})
                selected = radio_options[random.choice(radio_options)]

                form_data_payload[selected.get("name")] = selected.get("value")

            elif field_type == "checkbox":
                checkboxes = form.get("input", {"type": "checkbox"})
                selected = checkboxes[random.choice(checkboxes)]

                if selected.has_attr("value"):
                    form_data_payload[selected.get("name")] = selected.get("value")
                else:
                    form_data_payload[selected.get("name")] = "on"

        except AttributeError:
            # Some input attributes are blank or aren"t of  type "string",
            # which can"t be coerced; so, we just ignore the errors
            pass

        return form_data_payload

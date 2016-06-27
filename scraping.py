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


class LinkCrawler(object):
    """
        bla
    """
    url = ""
    cookies = {}
    exclude_patterns = []

    def __init__(self, url, cookies):
        self.cookies = cookies

        if url.startswith("/"):
            self.url = globalvars.BASE_URL + url
        else:
            self.url = url
        # print("LC " + self.url)

        with open(globalvars.EXCLUDE_URLS_FILE, "r") as exclude_patterns_file:
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

        print("FP " + self.url)

    def parse(self):
        """
            Finds all forms present in the page returned by the GET request,
            processes its fields and submits the form to the proper URL
        """

        request = requests.get(self.url, cookies=self.cookies)
        html_tree = request.text
        forms = BeautifulSoup(html_tree, "html.parser").find_all("form")

        for form in forms:
            form_data_payload = {}
            fields = form.find_all("input")

            for field in fields:
                pair_name_value = self.process_by_field_type(form, field)

                if pair_name_value is not None:
                    form_data_payload[pair_name_value[0]] = pair_name_value[1]

            submitter = Submitter(self.url, self.cookies, form.get("action"), form.get("method"), form_data_payload)
            submitter.submit()

    def process_by_field_type(self, form, field):
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
                    # Some input attributes are blank or aren"t of type
                    # "string", which can"t be coerced; so, we just ignore
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
            # Some input attributes are blank or aren"t of  type "string",
            # which can"t be coerced; so, we just ignore the errors
            pass

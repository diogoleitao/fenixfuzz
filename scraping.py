"""
    FenixEdu web scraping utility classes
"""
import requests
import string

from bs4 import BeautifulSoup

import globalvars
from Submitter import Submitter
from FuzzGenerator import FuzzGenerator


class LinkCrawler(object):
    """
        bla
    """
    url_seed = ""
    cookies = {}
    ignore_patterns = ["/logout", "/downloadFile"]

    def __init__(self, url_seed, cookies):
        self.url_seed = url_seed
        self.cookies = cookies

    def filter_url(self):
        """
            Checks if the url has only printable characters or if it contains
            a specific pattern. These patterns should be avoided, because
            the associated GET requests that may be performed have results
            that compromise the tool's flow.
        """

        has_strange_characters = not all(char in string.printable for char in self.url_seed)
        has_pattern_occurences = any(pattern in self.url_seed for pattern in self.ignore_patterns)

        return not has_strange_characters and not has_pattern_occurences

    def crawl(self):
        """
            Crawls the page returned by the GET request performed on the
            instance's url, looking for all the links the page has and adds each
            link if it's not present in the CRAWLED_LINKS_QUEUE global variable
        """
        filtered = self.filter_url()

        if filtered:
            # print self.url_seed
            request = requests.get(self.url_seed, cookies=self.cookies)
            html_tree = request.text
            anchors = BeautifulSoup(html_tree, 'html.parser').find_all('a')
            for anchor in anchors:
                href = anchor.get("href")
                try:
                    # Only save same domain links
                    if href.startswith(globalvars.COOKIES['contextPath']) or href.startswith(globalvars.BASE_URL):
                        if href not in globalvars.CRAWLED_LINKS_QUEUE:
                            # print "\t" + href
                            globalvars.CRAWLED_LINKS_QUEUE.append(href)
                            globalvars.LINKS_QUEUE.append(href)

                except AttributeError:
                    # Some href attributes are blank or aren't of type
                    # 'string', which can't be coerced; so, we just
                    # ignore the errors
                    continue


class FormParser(object):
    """
        bla
    """
    url = ""
    cookies = {}

    def __init__(self, url, cookies):
        self.url = url
        self.cookies = cookies

    def parse(self):
        """
            Parses
        """
        request = requests.get(self.url, cookies=self.cookies)
        html_tree = request.text
        forms = BeautifulSoup(html_tree, 'html.parser').find_all('form')
        for form in forms:
            form_data_payload = {}
            fields = form.find_all('input')
            hidden_fields = form.find_all('input', type='hidden')
            for hidden_field in hidden_fields:
                form_data_payload[hidden_field.get('name')] = hidden_field.get('value')
            for field in fields:
                field_type = field.get('type')
                try:
                    if field_type == 'hidden':
                        continue
                    else:
                        max_length = field.get('max')
                        min_length = field.get('min')
                        fuzz_generator = FuzzGenerator()
                        form_data_payload[field.get('name')] = fuzz_generator.generate(field_type, max_length, min_length)  # GENERATE FUZZ PATTERN --> EXTRACT GENERATOR TO A CLASS
                        print(field_type)
                except AttributeError:
                    # Some field type attributes are blank or aren't of
                    # type 'string', which can't be coerced; so, we
                    # just ignore the errors
                    continue
            submitter = Submitter(self.url, self.cookies, form.get('action'), form_data_payload, False)
            submitter.submit()

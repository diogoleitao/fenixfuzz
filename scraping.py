"""
    FenixEdu web scraping utility classes
"""
import requests
import string

from bs4 import BeautifulSoup

import globalvars


class LinkCrawler(object):
    """
        Sample docstring
    """
    url_seed = ""
    cookies = {}
    ignore_patterns = ["/logout", "/downloadFile"]

    def __init__(self, url_seed, cookies):
        if url_seed.startswith("/"):
            self.url_seed = globalvars.BASE_URL + url_seed
        else:
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
            Crawls
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
    """Sample docstring"""
    url = ""
    cookies = {}
    hidden_fields = []

    def __init__(self, url, cookies):
        # NEEDS TO BE PROCESSED THE SAME WAY AS THE
        # LINKCRAWLER. THIS, HOWEVER, SHOULD BE FIXED
        self.url = url
        self.cookies = cookies

    def parse(self):
        """Parses"""
        request = requests.get(self.url, cookies=self.cookies)
        html_tree = request.text
        forms = BeautifulSoup(html_tree, 'html.parser').find_all('form')
        for form in forms:
            fields = form.find_all('input')
            for field in fields:
                field_type = field.get('type')
                try:
                    if field_type == 'hidden':
                        self.hidden_fields.append(field)
                        print "hidden"
                        print "Not implemented"
                        continue
                    elif field_type == 'text' or field_type == 'textarea':
                        # Fill 'value' with fuzz patterns
                        print "text"
                        print "Not implemented"
                    else:
                        print "other"
                        print "Not implemented"
                except AttributeError:
                    # Some field type attributes are blank or aren't of
                    # type 'string', which can't be coerced; so, we
                    # just ignore the errors
                    continue

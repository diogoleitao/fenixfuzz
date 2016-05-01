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

    def __init__(self, url_seed, cookies):
        if url_seed.startswith("/"):
            self.url_seed = globalvars.BASE_URL + url_seed
        else:
            self.url_seed = url_seed
        self.cookies = cookies

    def filter_url(self):
        """
            Filters
        """
        has_strange_characters = not all(char in string.printable for char in self.url_seed)
        logout = "/logout" in self.url_seed
        download_file = "/downloadFile" in self.url_seed

        return not has_strange_characters and not logout and not download_file

    def crawl(self):
        """
            Crawls
        """
        filtered = self.filter_url()

        if filtered:
            print self.url_seed
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

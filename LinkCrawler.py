import requests
from bs4 import BeautifulSoup
import globalvars
import string


class LinkCrawler:
    url_seed = ""
    cookies = {}

    def __init__(self, url_seed, cookies):
        if url_seed.startswith("/"):
            self.url_seed = globalvars.base_url + url_seed
        else:
            self.url_seed = url_seed
        self.cookies = cookies

    def filterURL(self):
        has_strange_characters = not all(char in string.printable for char in self.url_seed)
        logout = "/logout" in self.url_seed
        download_file = "/downloadFile" in self.url_seed

        return not has_strange_characters and not logout and not download_file

    def crawl(self):
        ok = self.filterURL()

        if ok:
            print self.url_seed
            request = requests.get(self.url_seed, cookies=self.cookies)
            html_tree = request.text
            anchors = BeautifulSoup(html_tree, 'html.parser').find_all('a')
            for anchor in anchors:
                href = anchor.get("href")
                try:
                    # Only save same domain links
                    if href.startswith(globalvars.cookies['contextPath']) or href.startswith(globalvars.base_url):
                        if href not in globalvars.crawled_links_queue:
                            # print "\t" + href
                            globalvars.crawled_links_queue.append(href)
                            globalvars.links_queue.append(href)

                except AttributeError:
                    # Some href attributes are blank or aren't of type 'string',
                    # which can't be coerced; so, we just ignore the errors
                    continue

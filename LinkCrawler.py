import requests
from bs4 import BeautifulSoup
import globalvars


class LinkCrawler:
    url_seed = ""
    cookies = {}

    def __init__(self, url_seed, cookies):
        self.url_seed = globalvars.base_url + url_seed
        self.cookies = cookies

    def crawl(self):
        request = requests.get(self.url_seed, cookies=self.cookies)
        html_tree = request.text
        anchors = BeautifulSoup(html_tree, 'html.parser').find_all('a')
        for anchor in anchors:
            href = anchor.get("href")
            try:
                # Only save same domain links
                if href.startswith(globalvars.cookies['contextPath']) or href.startswith(globalvars.base_url):
                    if href not in globalvars.parsed_links_queue:
                        globalvars.parsed_links_queue.append(href)
                        globalvars.links_queue.append(href)

            except AttributeError:
                # Some href attributes are blank or aren't of type 'string',
                # which can't be coerced; so, we just ignore the errors
                continue

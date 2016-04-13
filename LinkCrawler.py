import requests
from bs4 import BeautifulSoup


class LinkCrawler:
    url_seed = ""
    cookies = {}

    def __init__(self, url_seed, cookies):
        self.url_seed = url_seed
        self.cookies = cookies
        return

    def crawl(self):
        # By declaring this variable as global, it enables direct access and
        # modification, instead of passing it as an argument and handling it
        # as a copy of the original queue.
        global links_queue
        global parsed_links_queue
        global list_changed

        page = requests.get(self.url_seed, cookies=self.cookies).text
        anchors = BeautifulSoup(page, 'html.parser').find_all('a')
        for anchor in anchors:
            href = anchor.get("href")
            try:
                if href.startswith("/"):  # Only save local links
                    if href not in parsed_links_queue:
                        parsed_links_queue.append(href)
                        links_queue.append(href)
                        list_changed = True

            except TypeError:
                # Some href attributes are blank or aren't of type 'string',
                # which can't be coerced; so, we just ignore the errors
                continue

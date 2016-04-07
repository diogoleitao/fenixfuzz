import requests
from collections import deque
from bs4 import BeautifulSoup


def crawler():
    links_queue = deque([])
    parsed_links_queue = deque([])
    home_url = "http://localhost:8080/starfleet/home.do"
    links_queue.append(home_url)

    request_url = "http://localhost:8080/starfleet/api/bennu-core/profile/login"
    response = requests.post(request_url, data={'username': 'SA1', 'password': ''})
    cookie_values = response.headers.get('set-cookie').replace(';', '').replace(',', '').split(' ')
    CONTEXT_PATH = cookie_values[0].split('=')[1]
    JSESSION_ID = cookie_values[2].split('=')[1]

    cookies = {
        'JSESSION_ID': JSESSION_ID,
        'contextPath': CONTEXT_PATH
    }

    parser(links_queue, cookies, parsed_links_queue)


def parser(links, cookies, queue):
    for url in links:
        page = requests.get(url, cookies=cookies).text
        link_elements = BeautifulSoup(page, 'html.parser').find_all('a')
        page_links = []
        for link in link_elements:
            anchor = link.get("href")
            try:
                if anchor.startswith("/"):
                    page_links.append(anchor)
            except TypeError:
                continue
        for page_link in page_links:
            if page_link not in links:
                links.append(page_link)
                queue.append(page_link)

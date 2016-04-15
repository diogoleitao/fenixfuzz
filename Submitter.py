import requests
import re


class Submitter:
    def __init__(self):
        return

    def submit(self, url, method, cookies, toPrint):
        request = None
        ok = False
        if method == "GET":
            request = requests.get(url, cookies=cookies)
            ok = True
        elif method == "PUT":
            request = requests.put(url, cookies=cookies)
            ok = True
        elif method == "POST":
            request = requests.post(url, cookies=cookies)
            ok = True

        if toPrint and ok:
            server_error_pattern = re.compile("^5[0-9][0-9]$")
            status_code = str(request.status_code)
            if server_error_pattern.match(status_code):
                return status_code + " " + url

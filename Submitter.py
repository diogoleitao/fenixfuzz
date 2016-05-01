"""Sample docstring"""
import re
import requests


class Submitter(object):
    """Sample docstring"""

    print_me = False

    def __init__(self, print_me):
        self.print_me = print_me
        return

    def submit(self, url, method, cookies):
        """Submits"""
        request = None
        request_status = False
        method = method.lower()
        if method == "GET":
            request = requests.get(url, cookies=cookies)
            request_status = True
        elif method == "POST":
            request = requests.post(url, cookies=cookies)
            request_status = True

        if self.print_me and request_status:
            server_error_pattern = re.compile("^5[0-9][0-9]$")
            status_code = str(request.status_code)
            if server_error_pattern.match(status_code):
                return status_code + " " + url

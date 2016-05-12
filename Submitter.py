"""Sample docstring"""
import re
import requests


class Submitter(object):
    """
        The Submitter class is responsible for sending the requests to the
        Fenix platform. Although this could be a simple function, in order to
        improve this tool's performance, this responsability was put into this
        module so that the submit() method can be used by "parallel" threads
    """

    url = ""
    cookies = {}
    action = ""
    form_payload = {}
    print_me = False

    def __init__(self, url, cookies, action, form_payload, print_me):
        self.url = url
        self.cookies = cookies
        self.action = action
        self.form_payload = form_payload
        self.print_me = print_me

    def submit(self):
        """
            Submits
        """
        request = None
        request_sent = False
        action = self.action.upper()
        if action == "GET":
            request = requests.get(self.url + self.action, cookies=self.cookies, data=self.form_payload)
            request_sent = True
        elif action == "POST":
            request = requests.post(self.url + self.action, cookies=self.cookies, data=self.form_payload)
            request_sent = True

        if self.print_me and request_sent:
            server_error_pattern = re.compile("^5[0-9][0-9]$")
            status_code = str(request.status_code)
            if server_error_pattern.match(status_code):
                print(status_code + " " + self.url)

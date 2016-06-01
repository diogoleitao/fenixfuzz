import re
import requests

import globalvars


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

    def __init__(self, url, cookies, action, form_payload):
        self.url = url
        self.cookies = cookies
        self.action = action
        self.form_payload = form_payload

    def submit(self):
        """
            Submits
        """
        request = None
        request_sent = False
        action = self.action.upper()
        final_url = globalvars.BASE_URL + self.action
        print(final_url)
        print(self.cookies)
        print(self.form_payload)
        if action == "GET":
            request = requests.get(final_url, cookies=self.cookies, data=self.form_payload)
            request_sent = True
        elif action == "POST":
            request = requests.post(final_url, cookies=self.cookies, data=self.form_payload)
            request_sent = True
        print(request)

        if request_sent:
            server_error_pattern = re.compile("^5[0-9][0-9]$")
            status_code = str(request.status_code)
            if server_error_pattern.match(status_code):
                print(status_code + " " + self.url)
        else:
            print("Request not sent")

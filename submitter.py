import re
import requests

import globalvars
from utils import printf


class Submitter(object):
    """
        The Submitter class is responsible for sending the requests to the
        Fenix platform. Although this could be a simple function, in order to
        improve this tool's performance, this responsability was put into this
        module so that the submit() method can be parallelized with threads.
    """

    def __init__(self, url, cookies, action, method, form_payload):
        self.url = url
        self.cookies = cookies
        self.action = action
        self.method = method
        self.form_payload = form_payload

    def submit(self):
        """
            Submits
        """

        if self.action is None:
            printf("Form at " + self.url + " does not have an explicit \"action\" url, so it can't be processed.")
            return

        request = None
        method = self.method.upper()
        final_url = globalvars.BASE_URL + self.action

        if method == "GET":
            request = requests.get(final_url, cookies=self.cookies, data=self.form_payload)
        elif method == "POST":
            request = requests.post(final_url, cookies=self.cookies, data=self.form_payload)
        self.check_request(request)

    def check_request(self, request):
        server_error_pattern = re.compile("^5[0-9][0-9]$")
        status_code = str(request.status_code)
        if server_error_pattern.match(status_code):
            print(status_code + " " + self.url)

        # html_tree = request.text
        # css_error_classes = ["has-error", "error0", "help-block"]
        # for error_class in css_error_classes:
        #     errors = BeautifulSoup(html_tree, "html.parser").find_all("div", class_=error_class)
        #     if len(errors) > 0:
        #         for error in errors:
        #             if error.has_attr("text"):
        #                 print(error.get("text"))
        #                 input()
        if not str(request.status_code).startswith("2"):
            print(request)

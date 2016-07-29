"""
    Submitter
"""

import re
import requests

from bs4 import BeautifulSoup

import globalvars
from report import build_error_data
import utils


class Submitter(object):
    """
        The Submitter class is responsible for sending the requests to the
        Fenix platform. Although this could be a simple function, in order to
        improve this tool's performance, this responsability was put into this
        module so that the submit() method can be parallelized with threads.
    """

    def __init__(self, url, cookies, form):
        self.url = url
        self.cookies = cookies
        self.form = form

    def submit(self):
        """
            Submits the form to the proper URL
        """

        if self.form.get_action() is None:
            globalvars.ERRORS.append(build_error_data(self, None, utils.NO_FORM_ACTION))
            return

        method = self.form.get_method().upper()
        final_url = globalvars.BASE_URL + self.form.get_action()

        form_payload = {}
        for field_info in self.form.get_fields():
            form_payload[field_info[0]] = field_info[2]

        if method == "GET":
            request = requests.get(final_url, cookies=self.cookies, data=form_payload)
        elif method == "POST":
            request = requests.post(final_url, cookies=self.cookies, data=form_payload)
        self.process_response(request)

    def process_response(self, request):
        """
            Registers if an error occurred
        """

        server_error_pattern = re.compile("^5[0-9][0-9]$")
        status_code = str(request.status_code)
        if server_error_pattern.match(status_code):
            globalvars.ERRORS.append(build_error_data(self, status_code, request.text))

        if 1 == 1:
            return

        #TODO
        html_tree = request.text
        css_error_classes = ["has-error", "error0", "help-block"]
        for error_class in css_error_classes:
            errors = BeautifulSoup(html_tree, "html.parser").find_all("div", class_=error_class)
            if len(errors) > 0:
                for error in errors:
                    if error.has_attr("text"):
                        print(error.get("text"))
                        input()
        if not str(request.status_code).startswith("2"):
            print(request)

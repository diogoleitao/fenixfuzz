"""
    Module is responsible for sending the requests to the Fenix
    platform.
"""

import re
import requests

from bs4 import BeautifulSoup

import globalvars
import utils
import report


def submit(form, cookies):
    """
        Submits the form to the proper URL
    """

    if form.action is None:
        error_data = report.build_error_data(form, None, utils.NO_FORM_ACTION)

        if form.url not in globalvars.ERRORS:
            globalvars.ERRORS[form.url] = []
        globalvars.ERRORS[form.url].append(error_data)
        return

    method = form.method.upper()
    final_url = globalvars.BASE_URL + form.action

    form_payload = {}
    for field_info in form.fields:
        form_payload[field_info[0]] = field_info[2]

    if method == "GET":
        response = requests.get(final_url, cookies=cookies, data=form_payload)

    elif method == "POST":
        response = requests.post(final_url, cookies=cookies, data=form_payload)

    elif method == "PUT":
        response = requests.put(final_url, cookies=cookies, data=form_payload)

    process_response(form, response)


def process_response(form, response):
    """
        Registers if an error occurred
    """

    cookies = response.headers.get("set-cookie")

    if cookies is None:
        cookies = response.headers.get("cookie")
    cookies = cookies.replace(";", "").replace(",", "").split(" ")

    new_ctx_path = cookies[0].split("=")[1]
    new_jsessionid = cookies[2].split("=")[1]

    if new_ctx_path != globalvars.COOKIES["contexPath"]:
        print("Context path after request doesn't match!")  # Error?

    if new_jsessionid != globalvars.COOKIES["JSESSIONID"]:
        print("Session cookie after request doesn't match!")  # Update?

    server_error_pattern = re.compile("^5[0-9][0-9]$")
    status_code = str(response.status_code)

    if server_error_pattern.match(status_code):
        error_data = report.build_error_data(form, status_code, response.text)

        if form.url not in globalvars.ERRORS:
            globalvars.ERRORS[form.url] = []
        globalvars.ERRORS[form.url].append(error_data)

    if 1 == 1:
        return

    # TODO
    html_tree = response.text
    css_error_classes = ["has-error", "error0", "help-block"]
    for error_class in css_error_classes:
        errors = BeautifulSoup(html_tree, "html.parser").find_all("div", class_=error_class)
        for error in errors:
            if error.has_attr("text"):
                print(error.get("text"))
                input()
    if not str(response.status_code).startswith("2"):
        print(response)

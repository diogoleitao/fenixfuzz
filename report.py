"""
    Report generation
"""

import json

import json2html

import globalvars


def build_field_data(submitter):
    """
        Creates a dictionary containing the fields' data
    """

    field_list = []
    for field_tuple in submitter.form.get_fields():
        field_data = {
            "name": field_tuple[0],
            "type": field_tuple[1],
            "value": field_tuple[2]
        }
        field_list.append(field_data)

    return field_list


def build_error_data(submitter, code, message):
    """
        Creates a dictionary containing the form's and error's data
    """

    return {
        "id": submitter.form.get_id(),
        "fields": build_field_data(submitter),
        "action": submitter.form.get_action(),
        "method": submitter.form.get_method(),
        "error": {
            "code": code,
            "message": message
        }
    }


def generate_html_report():
    """
        Generates HTML report file from JSON file
    """

    generate_json_report()

    # with open("output/report_test.html", "w") as report_file:
    json_data = None
    with open("output/report.json", "r") as json_file:
        json_data = json.loads(json_file.read())
    for data in json_data:
        url = data['url']

        forms = data['forms']
        for form in forms:
            fid = form['id']
            method = form['method']
            action = form['action']
            error_code = form['error']['code']
            error_message = form['error']['message']

            fields = form['fields']
            for field in fields:
                name = field['name']
                ftype = field['type']
                value = field['value']


def generate_json_report():
    """
        Generates JSON report file from the data gathered
    """

    with open("output/report.json", "w") as report_file:
        json.dump(globalvars.ERRORS, report_file)

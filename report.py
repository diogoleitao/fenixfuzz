"""
    Report generation
"""

import json

import globalvars


def build_field_data(submitter):
    """
        Creates an object containing the fields data
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
        Creates an object containing the form and error data
    """

    return {
        "id": submitter.form.get_id(),
        "fields": build_field_data(submitter),
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

    with open("report.html", "w") as report_file:
        with open("report.json", "r") as json_data:
            print(report_file)
            print(json_data)


def generate_json_report():
    """
        Generates JSON report file
    """

    with open("report.json", "w") as report_file:
        json.dump(globalvars.ERRORS, report_file)

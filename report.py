"""
    Report generation
"""

import json

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

    # generate_json_report()

    templates = load_templates()

    with open("output/report.json", "r") as json_file:
        json_data = json.loads(json_file.read())

    with open("output/report_test.html", "w") as report_file:
        report_file.write(templates[0].replace("{pages}", fill_page_templates(json_data, templates)))


def generate_json_report():
    """
        Generates JSON report file from the data gathered
    """

    with open("output/report.json", "w") as report_file:
        json.dump(globalvars.ERRORS, report_file)


def load_templates():
    """
        Reads the contents of each HTML template file and returns them as a tuple
    """

    with open("report-templates/report-main.html") as template:
        main = template.read()

    with open("report-templates/report-page.html") as template:
        page = template.read()

    with open("report-templates/report-form.html") as template:
        form = template.read()

    with open("report-templates/report-field.html") as template:
        field = template.read()

    return main, page, form, field


def fill_page_templates(pages, templates):
    """
        Substitute the URL and list of forms for all the pages
    """

    final_template = ""
    for page in pages:
        final_template += templates[1].replace("{url}", page['url']).replace("{forms}", fill_form_templates(page['forms'], templates))
    return final_template


def fill_form_templates(forms, templates):
    """
        Substitute the id, method, action, code message and list of fields for
        all the forms
    """

    final_template = ""
    for form in forms:
        final_template += templates[2].replace("{id}", form['id']).replace("{method}", form['method']).replace("{action}", form['action']).replace("{code}", form['error']['code']).replace("{message}", form['error']['message']).replace("{fields}", fill_field_templates(form['fields'], templates))
    return final_template


def fill_field_templates(fields, templates):
    """
        Substitute the name, type and value for all the fields
    """

    final_template = ""
    for field in fields:
        final_template += templates[3].replace("{name}", field['name']).replace("{type}", field['type']).replace("{value}", field['value'])
    return final_template

"""
    Report generation functions
"""

import json

import globalvars


def build_field_data(form):
    """
        Creates a dictionary containing the fields' data
    """

    field_list = []
    for field in form.fields:
        field_list.append({
            "name": field.name,
            "type": field.type,
            "value": field.value
        })

    return field_list


def build_error_data(form, code, message):
    """
        Creates a dictionary containing the form's and error's data
    """

    return {
        "fields": build_field_data(form),
        "action": form.action,
        "method": form.method,
        "error": {
            "code": code,
            "message": message
        }
    }


def generate_json_report():
    """
        Generates JSON report file from the data gathered
    """

    if globalvars.JSON_REPORT_FILE is None:
        output_dir = "output/report.json"
    else:
        output_dir = globalvars.JSON_REPORT_FILE

    final_data = []
    for url, form_data in globalvars.ERRORS.items():
        final_data.append({
            "url": url,
            "forms": form_data
        })

    with open(output_dir, "w") as report_file:
        json.dump(final_data, report_file)


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


def generate_html_report():
    """
        Generates HTML report file from JSON file
    """

    templates = load_templates()

    if globalvars.JSON_REPORT_FILE is None:
        output_dir_json = "output/report.json"
    else:
        output_dir_json = globalvars.JSON_REPORT_FILE

    if globalvars.GENERATE_HTML_REPORT:
        output_dir_html = globalvars.HTML_REPORT_FILE
    else:
        output_dir_html = "output/report.html"

    with open(output_dir_json, "r") as json_file:
        json_report = json.loads(json_file.read())

    with open(output_dir_html, "w") as report_file:
        report_file.write(templates[0].replace("{pages}", fill_page_template(json_report, templates)))


def fill_page_template(pages, templates):
    """
        Substitute the URL and list of forms for all the pages
    """

    final_template = ""
    for page in pages:
        final_template += (templates[1]
                           .replace("{url}", page['url'])
                           .replace("{forms}", fill_form_template(page['forms'], templates)))

    return final_template


def fill_form_template(forms, templates):
    """
        Substitute the method, action, code message and list of fields for all the forms
    """

    final_template = ""
    for form in forms:
        final_template += (templates[2]
                           .replace("{method}", form['method'])
                           .replace("{action}", form['action'])
                           .replace("{code}", form['error']['code'])
                           .replace("{message}", form['error']['message'])
                           .replace("{fields}", fill_fields_template(form['fields'], templates)))

    return final_template


def fill_fields_template(fields, templates):
    """
        Substitute the name, type and value for all the fields
    """

    final_template = ""
    for field in fields:
        final_template += (templates[3]
                           .replace("{name}", field['name'])
                           .replace("{type}", field['type'])
                           .replace("{value}", field['value']))

    return final_template

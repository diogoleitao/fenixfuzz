import requests
from bs4 import BeautifulSoup


class FormParser:
    url = ""
    cookies = {}
    hidden_fields = []

    def __init__(self, url, cookies):
        # TODO: PROBABLY NEEDS TO BE PROCESSED THE SAME WAY AS THE LINKCRAWLER
        #       THIS, HOWEVER, SHOULD BE FIXED
        self.url = url
        self.cookies = cookies

    def parse(self):
        request = requests.get(self.url, cookies=self.cookies)
        html_tree = request.text
        forms = BeautifulSoup(html_tree, 'html.parser').find_all('form')
        for form in forms:
            fields = forms.find_all('input')
            for field in fields:
                field_type = field.get('type')
                try:
                    if field_type == 'hidden':
                        self.hidden_fields.append(field)
                        print "hidden"
                        print "Not implemented"
                        continue
                    elif field_type == 'text' or field_type == 'textarea':
                        # TODO: fill 'value' with fuzz patterns
                        print "text"
                        print "Not implemented"
                    else:
                        print "other"
                        print "Not implemented"
                except AttributeError:
                    # Some field type attributes are blank or aren't of type
                    # 'string', which can't be coerced; so, we just ignore the
                    # errors
                    continue

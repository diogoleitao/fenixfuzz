import string
import random
import requests
import re

# Minimum string length
min_length = 1
# Maximum string length
max_length = 20
# List of generated strings to be feeded to the endpoints
garbage_strings = []


# Generates a string with a length of l containing random characters and/or numbers and/or symbols
def gen_garbage(length, mode):
    palette = ""
    if mode == 0:  # Characters, numbers and symbols
        palette = string.letters + string.digits
    elif mode == 1:  # Only characters and numbers
        palette = string.letters + string.digits
    elif mode == 2:  # Only characters
        palette = string.letters
    elif mode == 3:  # Only numbers
        palette = string.digits
    return ''.join(random.choice(palette) for i in range(length))

if __name__ == '__main__':
    print "Generating garbage..."
    for i in range(min_length, max_length + 1):
        garbage_strings.append(gen_garbage(i, 3))
    print "Done."
    print ""

    print "|---------------|"
    print "| GET endpoints |"
    print "|---------------|"
    get_endpoints = []
    with open("get_endpoints.in", "r") as get_endpoints_file:
        get_endpoints = get_endpoints_file.read().split("\n")
    for endpoint in get_endpoints:
        if "{id}" not in endpoint:
            http_request = requests.get(endpoint)
            print str(http_request.status_code) + " " + endpoint
        else:
            server_error_pattern = re.compile("^5[0-9][0-9]$")
            client_error_pattern = re.compile("^4[0-9][0-9]$")
            for fuzz_pattern in garbage_strings:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.get(final_endpoint)
                if server_error_pattern.match(str(http_request.status_code)) is not None or client_error_pattern.match(str(http_request.status_code)) is not None:
                    print str(http_request.status_code) + " " + final_endpoint
    print "Done."
    print ""

    print "|---------------|"
    print "| PUT endpoints |"
    print "|---------------|"
    put_endpoints = []
    with open("put_endpoints.in", "r") as put_endpoints_file:
        put_endpoints = put_endpoints_file.read().split("\n")
    for endpoint in put_endpoints:
        if "{id}" not in endpoint:
            http_request = requests.put(endpoint)
            print str(http_request.status_code) + " " + endpoint
        else:
            server_error_pattern = re.compile("^5[0-9][0-9]$")
            client_error_pattern = re.compile("^4[0-9][0-9]$")
            for fuzz_pattern in garbage_strings:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.put(final_endpoint)
                if server_error_pattern.match(str(http_request.status_code)) is not None or client_error_pattern.match(str(http_request.status_code)) is not None:
                    print str(http_request.status_code) + " " + final_endpoint
    print "Done."

    print "Nothing more to be tested. Exiting..."

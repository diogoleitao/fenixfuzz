import string
import random
import requests

# Minimum string length
min_length = 1
# Maximum string length
max_length = 20
# List of generated strings to be feeded to the endpoints
garbage_strings = []


def gen_garbage(length):  # Generates a string with a length of l containing random alphanumeric characters
    all_chars = string.letters + string.digits
    return ''.join(random.choice(all_chars) for i in range(length))

if __name__ == '__main__':
    # Initialize a list with values from min_gen_length to max_gen_length
    lengths = []
    print "Generating garbage..."
    for i in range(min_length, max_length + 1):
        garbage_strings.append(gen_garbage(i))
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
            for fuzz_pattern in garbage_strings:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.get(final_endpoint)
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
            for fuzz_pattern in garbage_strings:
                final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                http_request = requests.put(final_endpoint)
                print str(http_request.status_code) + " " + final_endpoint
    print "Done."

    print "Nothing more to be tested. Exiting..."

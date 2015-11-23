import string
import random
import requests

# Minimum string length
min_length = 1
# Maximum string length
max_length = 20
# List of generated strings to be feeded to the endpoints
strings = []


def gen_garbage(l):  # Generates a string with a length of l containing random alphanumeric characters
    chars = string.letters + string.digits
    return ''.join(random.choice(chars) for i in range(l))

if __name__ == '__main__':
    # Initialize a list with values from min_gen_length to max_gen_length
    lengths = []
    for i in range(min_length, max_length + 1):
        strings.append(gen_garbage(i))

    print "Testing GET endpoints..."
    get_endpoints = []
    with open("get_endpoints.in", "r") as get_endpoints_file:
        get_endpoints = get_endpoints_file.read().split("\n")
        for endpoint in get_endpoints:
            if "{id}" not in endpoint:
                request = requests.get(endpoint)
                print str(request.status_code) + " " + endpoint
            else:
                for fuzz_pattern in strings:
                    final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                    r = requests.get(final_endpoint)
                    print str(r.status_code) + " " + final_endpoint
    print "Done."
    print ""
    print "Testing PUT endpoints..."
    put_endpoints = []
    with open("put_endpoints.in", "r") as put_endpoints_file:
        put_endpoints = put_endpoints_file.read().split("\n")
        for endpoint in put_endpoints:
            if "{id}" not in endpoint:
                r = requests.put(endpoint)
                print str(r.status_code) + " " + endpoint
            else:
                for fuzz_pattern in strings:
                    final_endpoint = endpoint.replace("{id}", fuzz_pattern)
                    r = requests.put(final_endpoint)
                    print str(r.status_code) + " " + final_endpoint
    print "Done."

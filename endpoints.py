import requests


print "GET"
get_endpoints = []
with open("get_endpoints.in", "r") as get_endpoints_file:
    get_endpoints = get_endpoints_file.read().split("\n")
    for endpoint in get_endpoints:
        if "{id}" not in endpoint:
            r = requests.get(endpoint)
            if r.status_code == 404:
                print str(r.status_code) + " " + endpoint
        else:
            endpoint = endpoint.replace("{id}", str(1928374189))
            r = requests.get(endpoint)
            if r.status_code == 404:
                print str(r.status_code) + " " + endpoint

print "PUT"
put_endpoints = []
with open("put_endpoints.in", "r") as put_endpoints_file:
    put_endpoints = put_endpoints_file.read().split("\n")
    for endpoint in put_endpoints:
        if "{id}" not in endpoint:
            r = requests.put(endpoint)
            if r.status_code == 404:
                print str(r.status_code) + " " + endpoint
        else:
            endpoint = endpoint.replace("{id}", str(1928374189))
            r = requests.put(endpoint)
            if r.status_code == 404:
                print str(r.status_code) + " " + endpoint

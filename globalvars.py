"""
    Since Python only allows variables to be defined and not declared,
    all of them are assigned a "default" value, but that does not reflect
    its final value (that is, the value assigned when the script is
    running). This is avoided with the parse_input() function (see its
    documentation).
"""
from collections import deque

#
FORMS_QUEUE = deque([])
#
LINKS_QUEUE = deque([])
#
CRAWLED_LINKS_QUEUE = deque([])
#
COOKIES = {}
#
BASE_URL = "http://localhost:8080"
#
N_THREADS_CRAWLER = 1
#
N_THREADS_REQUESTS = 1
# Minimum fuzz pattern string length
MIN_LENGTH = 0
# Maximum fuzz pattern string length
MAX_LENGTH = 0
# Fuzz pattern generation mode
GMODE = ""
# If True, tests FenixEdu API
TEST_API = False
# Charset command line option
CHARSET = ""
# List of generated fuzz patterns
GARBAGE_STRINGS = []
# API version (only used if test_api is specified, to build the request URL)
API_VERSION = ""
# User role to perform login
USER_ROLE = ""

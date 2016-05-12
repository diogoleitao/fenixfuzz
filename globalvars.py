"""
    Since Python only allows variables to be defined and not declared,
    all of them are assigned a "default" value.However, that does not reflect
    their final value (that is, the value assigned when the script is
    running).
"""
from collections import deque

# Queue containing all the forms that were acquired after crawling
FORMS_QUEUE = deque([])
# Queue used for crawling Fenix and saving all the links found in a given webpage
LINKS_QUEUE = deque([])
# Queue containing all found links (no repetitions)
CRAWLED_LINKS_QUEUE = deque([])
# Cookies' dictionary, sent in every request
COOKIES = {}
# Local Fenix instance URL
BASE_URL = "http://localhost:8080"
# Number of threads to crawl "parallel"
N_THREADS_CRAWLER = 1
# Number of threads to execute "parallel" requests
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

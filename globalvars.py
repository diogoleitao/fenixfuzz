"""
    Since Python only allows variables to be defined and not declared,
    all of them are assigned a "default" value.However, that does not reflect
    their final value (that is, the value assigned when the script is
    running).
"""
from collections import deque

######################################################################
# VARIABLES WHOSE VALUES ARE READ FROM THE FENIXFUZZ.PROPERTIES FILE #
######################################################################
# Minimum fuzz pattern string length
MINIMUM = None
# Maximum fuzz pattern string length
MAXIMUM = None
# Fuzz pattern generation mode
GENMODE = None
# If True, tests FenixEdu API
TEST_API = None
# API version (only used if test_api is specified, to build the request URL)
API_VERSION = None
# Charset command line option
CHARSET = None
# User role to perform login
USER = None
# URLs to not be crawled
EXCLUDE_URLS_FILE = None
# Set of rules to generate input
FENIXFUZZ_MODEL_FILE = None
# Local instance context path
LOCAL_CONTEXT_PATH = None


# Queue containing all the forms acquired after crawling
FORMS_QUEUE = deque([])
# Queue used for crawling FenixEdu and saving all the links found in a given webpage
LINKS_QUEUE = deque([])
# Queue containing all found links (no duplicates)
CRAWLED_LINKS_QUEUE = deque([])
# Cookies' dictionary, sent in every request
COOKIES = {}
# Local Fenix instance URL
BASE_URL = "http://localhost:8080"
# List of generated fuzz patterns
GARBAGE_STRINGS = []
# Number of threads to crawl "parallel"
N_THREADS_CRAWLER = 1
# Number of threads to execute "parallel" requests
N_THREADS_REQUESTS = 1

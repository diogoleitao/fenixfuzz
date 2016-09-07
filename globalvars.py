"""
    Since Python only allows variables to be defined and not declared, all of
    them are assigned Python's None value (only the first batch).
"""

from collections import deque

##################################################################
###### VARIABLES READ (OR DERIVED) FROM FENIXFUZZ.PROPERTIES #####
##################################################################
# Minimum fuzz pattern string length
MINIMUM = None
# Maximum fuzz pattern string length
MAXIMUM = None
# Charset command line option
CHARSET = None
# User role to perform login
USER = None
# URLs to not be crawled
EXCLUDE_URLS_FILE = None
# Set of rules to generate input
FENIXFUZZ_MODEL_FILE = None
# Local instance context path (derived)
LOCAL_CONTEXT_PATH = None
# Crawler's starting page
START_PAGE = None
# Endpoint URL to perform login on local instance
LOGIN_ENDPOINT = None
# Local instance's base URL (derived)
BASE_URL = None
# Number of iterations
ITERATIONS = None


##################################################################
####################### AUXILIARY VARIABLES ######################
##################################################################
# Queue containing all the forms acquired after crawling
FORMS_QUEUE = deque([])
# Queue used for crawling FenixEdu and saving all the links found
LINKS_QUEUE = deque([])
# Queue containing all found links (no duplicates)
CRAWLED_LINKS_QUEUE = deque([])
# Cookies' dictionary, sent in every request
COOKIES = {}
# List of generated fuzz patterns
FUZZ_PATTERNS = []
# List of errors
ERRORS = {}

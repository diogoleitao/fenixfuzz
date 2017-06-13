"""
    Since Python only allows variables to be defined and not declared, all of them are assigned a
    default value
"""

from collections import deque

#########################################################
# VARIABLES READ (OR DERIVED) FROM FENIXFUZZ.PROPERTIES #
#########################################################
# Minimum fuzz pattern string length
MINIMUM = None
# Maximum fuzz pattern string length
MAXIMUM = None
# Fallback charset
CHARSET = None
# User role to perform login
USER = None
# Set of rules to generate input
FENIXFUZZ_MODEL = None
# Local instance context path (derived)
CONTEXT_PATH = None
# Crawler's starting page
START_PAGE = None
# Endpoint URL to perform login on local instance
LOGIN_ENDPOINT = None
# Local instance's base URL (derived)
BASE_URL = None
# Full path for the JSON report file
JSON_FILE_PATH = None
# Full path for the HTML report file
REPORT_FILE_PATH = None
# Output HTML report?
HTML_REPORT = None


#######################
# AUXILIARY VARIABLES #
#######################
# Queue containing all the forms acquired after crawling
FORMS_QUEUE = deque([])
# Queue used for crawling FenixEdu and saving all the links found
LINKS_QUEUE = deque([])
# Queue containing all found links (no duplicates)
CRAWLED_LINKS_QUEUE = deque([])
# Queue containing all the forms filled out, ready to be submitted
PARSED_FORMS_QUEUE = deque([])
# Cookies' dictionary, sent in every request
COOKIES = {}
# List of generated fuzz patterns
FUZZ_PATTERNS = []
# Errors found: dictionary between URL and list of forms
ERRORS = {}

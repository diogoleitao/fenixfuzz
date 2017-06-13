# FenixFuzz
FenixFuzz is a software fuzzer for [IST](https://tecnico.ulisboa.pt/)'s [FenixEdu](https://fenixedu.org/) system, developed within the scope of a MSc thesis. The main goal is to integrate this tool in the FenixEdu's development and build process, so that bugs are spotted earlier.

## Dependencies
- Python 3.x
- Beautiful Soup 4 (see [documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc))
- rstr 2.2.5 (see [documentation](https://pypi.python.org/pypi/rstr/2.2.5))

<!-- -->

	pip3 install beautifulsoup4
	pip3 install rstr

## Overview
1. FenixFuzz logs in through a local instance of FenixEdu with a given user and crawls every page it can reach;
2. For each page, retrieves its forms and fills them with fuzz patterns, either using generation-based or mutation-based fuzzing (see *Configuring FenixFuzz*);
3. After filling each form, the fuzzer submits it and saves the result.
4. Once it goes through all the forms that were found, the results are printed.

## Configuring FenixFuzz
The fuzzer's many properties and settings are configured via the *config/fenixfuzz.properties* file, which should be modified accordingly to each usage. Each one of the file's entries is explained below.

__*minimum/maximum*__: minimum/maximum size of the fuzz patterns to be generated. Each value should be greater than 0.

	minimum = 1
	maximum = 20

__*charset*__:  charset to be used when the *fenixfuzz_model* file has no rules at all, as a fallback value or as a starting point for fields that are not covered by the rules in the JSON file. Accepted values are *all* (Python's printable characters), *no-white*, *alpha*, *char* and *num*.

	charset = alpha

__*user*__: user ID used to log in the application. Different types of users will allow the fuzzer to crawl different parts of FenixEdu, thus testing fewer or more of its forms.

	user = ist123456

__*url_patterns*__: path to JSON file containing an object with two lists: all the URLs that should be ignored during the crawling phase and URLs that should only be visited once. The first list is to prevent the fuzzer from crawling URLs that may invalidate the current cookie data (logout pages or similar) or file URLs (such as PDFs), which can't be fuzzed; the second list is for links of pages which provide the same type of information (e.g. room scheduling, student information) and need only to be visited once.

	url_patterns = config/url_patterns.json

__*fenixfuzz_model*__: path to JSON file containing a set of rules (regular expressions, or similar) that describe what is to be generated when a certain field name pattern is found. For example, if a field's name is *email*, then a possible rule for it could be *[a-zA-Z]+\@tecnico.ulisboa.pt*".

	fenixfuzz_model = config/ffm.json

__*local_instance*__: complete URL of the local running instance.

	local_instance = http://localhost:8080/fenix

__*login_endpoint*__: local API's endpoint to where the login data is sent.

	login_endpoint = /api/bennu-core/profile/login

# FenixFuzz
FenixFuzz is a software fuzzer for [IST](http://tecnico.ulisboa.pt/)'s FenixEdu system, developed within the scope of a MSc thesis. The main goal is to integrate this tool in the FenixEdu's development and build process, so that bugs are spotted earlier.

## Overview
1. FenixFuzz logs in through a local instance of [FenixEdu](http://fenixedu.org/) with a given user and crawls every page it can reach;
2. For each page, retrieves its forms and fills them with fuzz patterns, either using generation-based or mutation-based fuzzing (see *Configuring FenixFuzz*);
3. After filling each form, the fuzzer submits it and prints the result obtained.
4. (Optional) If specified in the *.properties* file (under *config/*), FenixFuzz also tests the FenixEdu's [API](https://fenixedu.org/dev/api/).

## Configuring FenixFuzz
The fuzzer's many properties and settings are configured via the *config/fenixfuzz.properties* file, which should be modified accordingly to each usage. Each one of the file's entries is explained below.

*minimum/maximum*: minimum/maximum size of the fuzz patterns to be generated. Each value should be greater than 0.

    minimum = 1
    maximum = 20

*genmode*: it specifies how the fuzz patterns are generated. Generation-based fuzzing consists of constructing a string from a set of characters (for example) and discarding the string used. Mutation-based fuzzing starts from a known-good input, mutates and reuses it (after sending it to the target application) if the result obtained (from the submission) respects a certain heuristic. Accepted values are either *generation* or *mutation*.

    genmode = generation

*test_api*: if the value is [y]es, then the FenixEdu's API is tested. If it's [n]o, then only the web platform is fuzzed.

    test_api = y

*charset*:  TBD

    charset = alpha

*user*: the user ID used to login to the application. Different types of users will allow the fuzzer to crawl different parts of FenixEdu.

    user = ist123456

*exclude_urls*: a JSON file containing a list of all the URLs that should be ignored during the crawling phase. This is to prevent the fuzzer from crawling URLs that may invalidate the current cookie data (logout procedures or similar), file URLs (such as PDFs) or links which provide the same type of information (e.g., room scheduling). The latter will be checked by analyzing a sample of said links to deduce the overall outcome.

    exclude_urls = config/exclude.json

*fenixfuzz_model*: a JSON file containing a set of rules (regular expressions, or similar) which describes what is to be generated when a certain pattern of field name is found. For example, if a field's name is *email*, then a possible rule for it could be *[a-zA-Z]+\@ist.utl.pt*".

    fenixfuzz_model = config/ffm.json

*local_instance*: the URL of the local running instance.

    local_instance = http://localhost:8080/fenix

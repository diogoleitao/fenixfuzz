# FenixFuzz
FenixFuzz is a software fuzzer for [IST](http://tecnico.ulisboa.pt/)'s FenixEdu system, developed within the scope of a MSc thesis. The main goal is to integrate this tool in the FenixEdu's development and build process, so that bugs are spotted earlier.

## Overview
1. FenixFuzz logs in through a local instance of [FenixEdu](http://fenixedu.org/) with a given user and crawls every page it can reach;
2. For each page, retrieves the associated forms and fills them with fuzz patterns, either using generation-based or mutation-based fuzzing (see *Configuring FenixFuzz*);
3. After filling each form, the fuzzer submits it and prints the result obtained.
4. (Optional) If specified in the *.properties* file (under *config/*), FenixFuzz may also test the FenixEdu's [API](https://fenixedu.org/dev/api/).

## Configuring FenixFuzz
The fuzzer's many properties and settings are configured via the *config/fenixfuzz.properties* file, which should be modified accordingly to each usage. Each one of the file's entries is explained below.

*minimum/maximum*: minimum/maximum size of the fuzz patterns to be generated. Each value should be greater than 0.

    minimum = 1
    maximum = 20

*genmode*: it specifies how the fuzz patterns are generated. Accepted values are either *generation* or *mutation*.

    genmode = generation

*test_api*: if its value is [y]es, then the FenixEdu's API is tested as well. If it's [n]o, then only the web platform is fuzzed.

    test_api = y

*charset*:  TBD

    charset = alpha

*user*: TBD

    user = ist123456

*exclude_urls*: TBD

    exclude_urls = config/exclude.json

*fenixfuzz_model*: TBD

    fenixfuzz_model = config/ffm.json

*local_context_path*: TBD

    local_context_path = http://localhost:8080/fenix

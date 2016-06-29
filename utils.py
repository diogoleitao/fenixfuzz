import sys


def read_properties_file(path, sep=" = ", comment_char="#"):
    """
        Reads the .properties file and parses its values. If any error occurs,
        it prints a message and kills the program.
    """
    try:
        props = {}
        with open(path, "r") as properties_file:
            for line in properties_file:
                line = line.strip()
                if line and not line.startswith(comment_char):
                    key_value = line.split(sep)
                    props[key_value[0].strip()] = key_value[1].strip("\" \t")
        return props
    except OSError:
        terminate("Please check that \"" + path + "\" is correct/exists.", 1)


def printf(message, end="\n"):
    """
        A custom alternative to Python's builtin print function
    """
    sys.stdout.write(str(message) + end)
    sys.stdout.flush()


def terminate(message, code):
    """
        Prints a message and exits the main program with the given error code
    """
    if code == 1:
        printf("ERROR:\n\t" + message)
    else:
        printf(message)
    sys.exit(code)

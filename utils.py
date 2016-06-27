import sys


def printf(message, end="\n"):
    sys.stdout.write(str(message) + end)
    sys.stdout.flush()


def terminate(message, code):
    if code == 1:
        printf("ERROR:\n\t" + message)
    else:
        printf(message)
    sys.exit(code)

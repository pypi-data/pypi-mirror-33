import sys

PYTHON_VERSION_2 = 2


def is_python_2():
    return sys.version_info.major == PYTHON_VERSION_2

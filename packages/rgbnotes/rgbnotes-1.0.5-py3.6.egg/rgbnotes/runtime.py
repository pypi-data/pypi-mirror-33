import sys


class runtime_info:
    OS_LINUX = (sys.platform.startswith('linux'))
    OS_DARWIN = (sys.platform == 'darwin')
    OS_WIN = (sys.platform == 'win32')
    PYTHON_2 = (sys.version_info.major == 2)
    PYTHON_3 = (sys.version_info.major == 3)


def python_version():
    return '{}.{}.{}'.format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)

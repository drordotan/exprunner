
from . import logger
from . import experiment
from . import xlsreader
from . import parser
from . import generator
from . import compile


def version():
    return 1, 0, 2


def version_str():
    v = version()
    return "{}.{}.{}".format(v[0], v[1], v[2])

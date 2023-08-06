import os
import sys
from glob import glob
from ctypes import c_double, c_float, CDLL

DOUBLE = c_float #: floating point precision

DIR = os.path.dirname(__file__)

PATH = os.path.abspath(os.path.join(DIR, "astrohutc*"))
PATH = glob(PATH)
for path in PATH:
    if ".py" in path:
        pass
    else:
        PATH = path
        break

LIB = CDLL(PATH) #: CDLL instance of the shared library

import sys
if sys.version_info[0] > 2:
    raise Exception("You have to use Python 2")

from .fingerpi import FingerPi


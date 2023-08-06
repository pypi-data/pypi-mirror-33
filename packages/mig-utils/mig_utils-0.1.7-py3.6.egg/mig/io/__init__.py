import sys
from ._io import *
# async/await requires python 3.5
if sys.version_info[:2] >= (3, 5):
    from ._async_io import *

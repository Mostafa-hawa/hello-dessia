import pkg_resources
from .core import *
__version__ = pkg_resources.require("test_1")[0].version

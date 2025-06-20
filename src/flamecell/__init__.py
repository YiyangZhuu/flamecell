# read version from installed package
from importlib.metadata import version
from .sim_utils import *
__version__ = version("flamecell")
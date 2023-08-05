# encoding: utf-8

# Get module version
from ._metadata import __version__

# Import key items from module
from .time_constants import *
from .timers import Timeout, Stopwatch, Throttle

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())

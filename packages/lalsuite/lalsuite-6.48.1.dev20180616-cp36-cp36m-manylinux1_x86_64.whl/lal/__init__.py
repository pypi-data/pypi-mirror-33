# Import SWIG wrappings, if available
from .lal import *

__version__ = "6.18.0.1"

## \addtogroup lal_python
"""This package provides Python wrappings and extensions to LAL"""

#
# =============================================================================
#
#                        CachedDetectors Look-up Tables
#
# =============================================================================
#


cached_detector_by_prefix = dict((cd.frDetector.prefix, cd) for cd in CachedDetectors)
# make sure there were no duplicates
assert len(cached_detector_by_prefix) == len(CachedDetectors)


cached_detector_by_name = dict((cd.frDetector.name, cd) for cd in CachedDetectors)
# make sure there were no duplicates
assert len(cached_detector_by_name) == len(CachedDetectors)


name_to_prefix = dict((name, detector.frDetector.prefix) for name, detector in cached_detector_by_name.items())
prefix_to_name = dict((prefix, name) for name, prefix in name_to_prefix.items())

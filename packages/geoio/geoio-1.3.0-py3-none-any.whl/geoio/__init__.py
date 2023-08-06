import imp as _imp
import logging as _logging

# Pull in main modules/classes
from geoio.base import GeoImage
from geoio.dg import DGImage
import geoio.constants
import geoio.utils
import os
#import downsample  # numba compile is trigger at import and it necessarily slow

_logger = _logging.getLogger(__name__)

# Pull in optional modules
try:
    from geoio_dlext import DLImage
    from geoio_dlext import constants_dl
except:
    pass

# Maybe move as much of this as possible into the plotting routine and just do:
# try:
#     import plotting
# except:
#     pass
try:
    _imp.find_module('matplotlib')
    import matplotlib
    display_flag = "DISPLAY" in os.environ
    if not display_flag:
        matplotlib.use('Agg')
    else:
        pass
    from . import plotting
except:
    _logger.info('plotting is not available from geoio - matplotlib is missing.')
    pass

# Import version number
from ._version import __version__

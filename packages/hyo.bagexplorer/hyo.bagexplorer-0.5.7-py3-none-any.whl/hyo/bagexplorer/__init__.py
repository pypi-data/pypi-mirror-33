"""
Hydro-Package
BAG Explorer
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

__version__ = '0.5.7'
__doc__ = 'BAG Explorer'
__author__ = 'gmasetti@ccom.unh.edu, brc@ccom.unh.edu'
__license__ = 'LGPLv3 license'
__copyright__ = 'Copyright (c) 2018, University of New Hampshire, Center for Coastal and Ocean Mapping'


def hyo_app():
    return __doc__, __version__


# def hyo_lib():
#     return __doc__, __version__


def hyo_favicon():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "media", "hyo_button.png"))

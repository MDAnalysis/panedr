# -*- coding: utf-8 -*-

import pbr.version
__version__ = pbr.version.VersionInfo('pyedr').release_string()
del pbr

from .pyedr import edr_to_dict, read_edr

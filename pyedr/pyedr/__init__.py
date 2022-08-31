# -*- coding: utf-8 -*-
from .pyedr import edr_to_dict, read_edr, get_unit_dictionary
import pbr.version
__version__ = pbr.version.VersionInfo('pyedr').release_string()
del pbr

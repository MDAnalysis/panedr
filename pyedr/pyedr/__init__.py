# -*- coding: utf-8 -*-
from .pyedr import ENX_VERSION, edr_to_dict, read_edr, get_unit_dictionary
import pbr.version
__version__ = pbr.version.VersionInfo('pyedr').release_string()
del pbr

# export `ENX_VERSION` for version checking in tests
# this is not useful for normal use
__all__ = ['ENX_VERSION', 'edr_to_dict', 'read_edr', 'get_unit_dictionary']

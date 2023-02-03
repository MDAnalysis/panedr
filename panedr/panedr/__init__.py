# -*- coding: utf-8 -*-
import pbr.version
from .panedr import ENX_VERSION, edr_to_df, get_unit_dictionary
__version__ = pbr.version.VersionInfo('panedr').release_string()
del pbr

# export `ENX_VERSION` for version checking in tests
# this is not useful for normal use
__all__ = ['ENX_VERSION', 'edr_to_df', 'get_unit_dictionary']

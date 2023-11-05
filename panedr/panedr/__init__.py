# -*- coding: utf-8 -*-
from .panedr import ENX_VERSION, edr_to_df, get_unit_dictionary
from importlib.metadata import version
__version__ = version("panedr")

# export `ENX_VERSION` for version checking in tests
# this is not useful for normal use
__all__ = ['ENX_VERSION', 'edr_to_df', 'get_unit_dictionary']

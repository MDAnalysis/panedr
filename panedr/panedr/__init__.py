# -*- coding: utf-8 -*-
from .panedr import edr_to_df, get_unit_dictionary
import pbr.version
__version__ = pbr.version.VersionInfo('panedr').release_string()
del pbr

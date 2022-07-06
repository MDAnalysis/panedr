# -*- coding: utf-8 -*-

import pbr.version
__version__ = pbr.version.VersionInfo('panedrlite').release_string()
del pbr

from .panedr import edr_to_df, edr_to_dict, read_edr

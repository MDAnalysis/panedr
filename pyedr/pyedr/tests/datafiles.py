# -*- coding:utf-8 -*-
# PyEDR -- a library to manipulate Gromacs EDR file in python
# Copyright (C) 2022  Jonathan Barnoud
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301  USA

# Move to impportlib.resources when py>=3.7
from pkg_resources import resource_filename

from pathlib import Path


EDR = resource_filename(__name__, 'data/cat_small.edr')
EDR_XVG = resource_filename(__name__, 'data/cat_small.xvg')
EDR_UNITS = resource_filename(__name__, 'data/cat_small_units.p')

EDR_IRREG = resource_filename(__name__, 'data/irregular.edr')
EDR_IRREG_XVG = resource_filename(__name__, 'data/irregular.xvg')
EDR_IRREG_UNITS = resource_filename(__name__, 'data/irregular_units.p')

EDR_DOUBLE = resource_filename(__name__, 'data/double.edr')
EDR_DOUBLE_XVG = resource_filename(__name__, 'data/double.xvg')
EDR_DOUBLE_UNITS = resource_filename(__name__, 'data/double_units.p')

EDR_BLOCKS = resource_filename(__name__, 'data/blocks.edr')
EDR_BLOCKS_XVG = resource_filename(__name__, 'data/blocks.xvg')
EDR_BLOCKS_UNITS = resource_filename(__name__, 'data/blocks_units.p')

# Testfiles for file version 1 with single precision
# See GROMACS regressiontests `Initial revision` (96c57f0d)
# http://redmine.gromacs.org/projects/regressiontests
EDR_V1 = resource_filename(__name__, 'data/1.edr')
EDR_V1_XVG = resource_filename(__name__, 'data/1.xvg')
EDR_V1_UNITS = resource_filename(__name__, 'data/1_units.p')

# Testfiles for file version 1 with double precision
# See GROMACS regressiontests `Initial revision` (96c57f0d)
# http://redmine.gromacs.org/projects/regressiontests
EDR_V1_DOUBLE = resource_filename(__name__, 'data/1_d.edr')
EDR_V1_DOUBLE_XVG = resource_filename(__name__, 'data/1_d.xvg')
EDR_V1_DOUBLE_UNITS = resource_filename(__name__, 'data/1_d_units.p')

# Testfiles for file version 2
# Generated from GROMACS regression test 'simple/imp1'
# at branch 'release-4-5'
# See https://gitlab.com/gromacs/gromacs-regressiontests
# GROMACS version commit bcbfcdee8e449344605552fa90c18eeab2b1fc53
EDR_V2 = resource_filename(__name__, 'data/2.edr')
EDR_V2_XVG = resource_filename(__name__, 'data/2.xvg')
EDR_V2_UNITS = resource_filename(__name__, 'data/234_units.p')
EDR_V2_DOUBLE = resource_filename(__name__, 'data/2_d.edr')
EDR_V2_DOUBLE_XVG = resource_filename(__name__, 'data/2_d.xvg')
EDR_V2_DOUBLE_UNITS = resource_filename(__name__, 'data/234_units.p')

# Testfiles for file version 3
# Generated from GROMACS regression test 'simple/imp1'
# at branch 'release-4-5'
# See https://gitlab.com/gromacs/gromacs-regressiontests
# GROMACS version commit d9c1da8c98ef7a99db5de71c57f683cf19435ef5
EDR_V3 = resource_filename(__name__, 'data/3.edr')
EDR_V3_XVG = resource_filename(__name__, 'data/3.xvg')
EDR_V3_UNITS = resource_filename(__name__, 'data/234_units.p')
EDR_V3_DOUBLE = resource_filename(__name__, 'data/3_d.edr')
EDR_V3_DOUBLE_XVG = resource_filename(__name__, 'data/3_d.xvg')
EDR_V3_DOUBLE_UNITS = resource_filename(__name__, 'data/234_units.p')

# Testfiles for file version 4
# Generated from GROMACS regression test 'simple/imp1'
# at branch 'release-4-5'
# See https://gitlab.com/gromacs/gromacs-regressiontests
# GROMACS version commit 5d24334a33745dbf26f2904badcb3c4989e087d3
EDR_V4 = resource_filename(__name__, 'data/4.edr')
EDR_V4_XVG = resource_filename(__name__, 'data/4.xvg')
EDR_V4_UNITS = resource_filename(__name__, 'data/234_units.p')
EDR_V4_DOUBLE = resource_filename(__name__, 'data/4_d.edr')
EDR_V4_DOUBLE_XVG = resource_filename(__name__, 'data/4_d.xvg')
EDR_V4_DOUBLE_UNITS = resource_filename(__name__, 'data/234_units.p')

# Collection of testfiles and corresponding reference data as a tuple.
# A tuple contains paths for the testfile, expected values in a XVG file,
# a serialized unit dictionary, and the EDR version number in this order.
TESTFILE_PARAMS = [
    (EDR, EDR_XVG, EDR_UNITS, 5),
    (EDR_IRREG, EDR_IRREG_XVG, EDR_IRREG_UNITS, 5),
    (EDR_DOUBLE, EDR_DOUBLE_XVG, EDR_DOUBLE_UNITS, 5),
    (EDR_BLOCKS, EDR_BLOCKS_XVG, EDR_BLOCKS_UNITS, 5),
    (EDR_V1, EDR_V1_XVG, EDR_V1_UNITS, 1),
    (EDR_V1_DOUBLE, EDR_V1_DOUBLE_XVG, EDR_V1_DOUBLE_UNITS, 1),
    (EDR_V2, EDR_V2_XVG, EDR_V2_UNITS, 2),
    (EDR_V2_DOUBLE, EDR_V2_DOUBLE_XVG, EDR_V2_DOUBLE_UNITS, 2),
    (EDR_V3, EDR_V3_XVG, EDR_V3_UNITS, 3),
    (EDR_V3_DOUBLE, EDR_V3_DOUBLE_XVG, EDR_V3_DOUBLE_UNITS, 3),
    (EDR_V4, EDR_V4_XVG, EDR_V4_UNITS, 4),
    (EDR_V4_DOUBLE, EDR_V4_DOUBLE_XVG, EDR_V4_DOUBLE_UNITS, 4),
    (Path(EDR), EDR_XVG, EDR_UNITS, 5),
    ]

EDR_MOCK_V1_ESUM0 = resource_filename(__name__, 'data/mocks/v1_nre2_esum0.edr')
EDR_MOCK_V5_STEP_NEGATIVE = resource_filename(
    __name__, 'data/mocks/v5_step_negative.edr'
)
EDR_MOCK_V1_STEP_NEGATIVE = resource_filename(
    __name__, 'data/mocks/v1_step_negative.edr'
)
EDR_MOCK_V_LARGE = resource_filename(__name__, 'data/mocks/v_large.edr')
EDR_MOCK_V4_LARGE_VERSION_FRAME = resource_filename(
    __name__, 'data/mocks/v4_large_version_frame.edr'
)
EDR_MOCK_V4_FIRST_REAL_V1 = resource_filename(
    __name__, 'data/mocks/v4_first_real_v1.edr'
)
EDR_MOCK_V4_INVALID_FILE_MAGIC = resource_filename(
    __name__, 'data/mocks/v4_invalid_file_magic.edr'
)
EDR_MOCK_V4_INVALID_FRAME_MAGIC = resource_filename(
    __name__, 'data/mocks/v4_invalid_frame_magic.edr'
)
EDR_MOCK_V4_INVALID_BLOCK_TYPE = resource_filename(
    __name__, 'data/mocks/v4_invalid_block_type.edr'
)
EDR_MOCK_V4_ALL_BLOCK_TYPES = resource_filename(
    __name__, 'data/mocks/v4_all_block_types.edr'
)
EDR_MOCK_V3_NDISRE2_BLOCKS = resource_filename(
    __name__, 'data/mocks/v3_ndisre2_blocks.edr'
)

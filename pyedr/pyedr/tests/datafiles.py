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

from importlib import resources

from pathlib import Path


_data_ref = resources.files('pyedr.tests.data')

EDR = (_data_ref / 'cat_small.edr').as_posix()
EDR_XVG = (_data_ref /  'cat_small.xvg').as_posix()
EDR_UNITS = (_data_ref /  'cat_small_units.p').as_posix()

EDR_IRREG = (_data_ref /  'irregular.edr').as_posix()
EDR_IRREG_XVG = (_data_ref /  'irregular.xvg').as_posix()
EDR_IRREG_UNITS = (_data_ref /  'irregular_units.p').as_posix()

EDR_DOUBLE = (_data_ref /  'double.edr').as_posix()
EDR_DOUBLE_XVG = (_data_ref /  'double.xvg').as_posix()
EDR_DOUBLE_UNITS = (_data_ref /  'double_units.p').as_posix()

EDR_BLOCKS = (_data_ref /  'blocks.edr').as_posix()
EDR_BLOCKS_XVG = (_data_ref /  'blocks.xvg').as_posix()
EDR_BLOCKS_UNITS = (_data_ref /  'blocks_units.p').as_posix()

# Testfiles for file version 1 with single precision
# See GROMACS regressiontests `Initial revision` (96c57f0d)
# http://redmine.gromacs.org/projects/regressiontests
EDR_V1 = (_data_ref /  '1.edr').as_posix()
EDR_V1_XVG = (_data_ref /  '1.xvg').as_posix()
EDR_V1_UNITS = (_data_ref /  '1_units.p').as_posix()

# Testfiles for file version 1 with double precision
# See GROMACS regressiontests `Initial revision` (96c57f0d)
# http://redmine.gromacs.org/projects/regressiontests
EDR_V1_DOUBLE = (_data_ref /  '1_d.edr').as_posix()
EDR_V1_DOUBLE_XVG = (_data_ref /  '1_d.xvg').as_posix()
EDR_V1_DOUBLE_UNITS = (_data_ref /  '1_d_units.p').as_posix()

# Testfiles for file version 2
# Generated from GROMACS regression test 'simple/imp1'
# at branch 'release-4-5'
# See https://gitlab.com/gromacs/gromacs-regressiontests
# GROMACS version commit bcbfcdee8e449344605552fa90c18eeab2b1fc53
EDR_V2 = (_data_ref /  '2.edr').as_posix()
EDR_V2_XVG = (_data_ref /  '2.xvg').as_posix()
EDR_V2_UNITS = (_data_ref /  '234_units.p').as_posix()
EDR_V2_DOUBLE = (_data_ref /  '2_d.edr').as_posix()
EDR_V2_DOUBLE_XVG = (_data_ref /  '2_d.xvg').as_posix()
EDR_V2_DOUBLE_UNITS = (_data_ref /  '234_units.p').as_posix()

# Testfiles for file version 3
# Generated from GROMACS regression test 'simple/imp1'
# at branch 'release-4-5'
# See https://gitlab.com/gromacs/gromacs-regressiontests
# GROMACS version commit d9c1da8c98ef7a99db5de71c57f683cf19435ef5
EDR_V3 = (_data_ref /  '3.edr').as_posix()
EDR_V3_XVG = (_data_ref /  '3.xvg').as_posix()
EDR_V3_UNITS = (_data_ref /  '234_units.p').as_posix()
EDR_V3_DOUBLE = (_data_ref /  '3_d.edr').as_posix()
EDR_V3_DOUBLE_XVG = (_data_ref /  '3_d.xvg').as_posix()
EDR_V3_DOUBLE_UNITS = (_data_ref /  '234_units.p').as_posix()

# Testfiles for file version 4
# Generated from GROMACS regression test 'simple/imp1'
# at branch 'release-4-5'
# See https://gitlab.com/gromacs/gromacs-regressiontests
# GROMACS version commit 5d24334a33745dbf26f2904badcb3c4989e087d3
EDR_V4 = (_data_ref /  '4.edr').as_posix()
EDR_V4_XVG = (_data_ref /  '4.xvg').as_posix()
EDR_V4_UNITS = (_data_ref /  '234_units.p').as_posix()
EDR_V4_DOUBLE = (_data_ref /  '4_d.edr').as_posix()
EDR_V4_DOUBLE_XVG = (_data_ref /  '4_d.xvg').as_posix()
EDR_V4_DOUBLE_UNITS = (_data_ref /  '234_units.p').as_posix()

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

EDR_MOCK_V1_ESUM0 = (_data_ref /  'mocks/v1_nre2_esum0.edr').as_posix()
EDR_MOCK_V5_STEP_NEGATIVE = (_data_ref / 'mocks/v5_step_negative.edr').as_posix()
EDR_MOCK_V1_STEP_NEGATIVE = (_data_ref / 'mocks/v1_step_negative.edr').as_posix()
EDR_MOCK_V_LARGE = (_data_ref /  'mocks/v_large.edr').as_posix()
EDR_MOCK_V4_LARGE_VERSION_FRAME = (_data_ref /  'mocks/v4_large_version_frame.edr').as_posix()
EDR_MOCK_V4_FIRST_REAL_V1 = (_data_ref /  'mocks/v4_first_real_v1.edr').as_posix()
EDR_MOCK_V4_INVALID_FILE_MAGIC = (_data_ref /  'mocks/v4_invalid_file_magic.edr').as_posix()
EDR_MOCK_V4_INVALID_FRAME_MAGIC = (_data_ref /  'mocks/v4_invalid_frame_magic.edr').as_posix()
EDR_MOCK_V4_INVALID_BLOCK_TYPE = (_data_ref /  'mocks/v4_invalid_block_type.edr').as_posix()
EDR_MOCK_V4_ALL_BLOCK_TYPES = (_data_ref /  'mocks/v4_all_block_types.edr').as_posix()
EDR_MOCK_V3_NDISRE2_BLOCKS = (_data_ref /  'mocks/v3_ndisre2_blocks.edr').as_posix()

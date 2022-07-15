#-*- coding:utf-8 -*-
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

__all__ = [
    "EDR", "EDR_XVG",  # all EDR fields read with ``gmx energy``
    "EDR_IRREGULAR", "EDR_IRREGULAR_XVG",
    "EDR_DOUBLE", "EDR_DOUBLE_XVG",
    "EDR_BLOCKS", "EDR_BLOCKS_XVG",
]

# Move to impportlib.resources when py>=3.7
from pkg_resources import resource_filename


EDR = resource_filename(__name__, 'data/cat.edr')
EDR_XVG = resource_filename(__name__, 'data/cat.xvg')

EDR_IRREGULAR = resource_filename(__name__, 'data/irregular.edr')
EDR_IRREGULAR_XVG = resource_filename(__name__, 'data/irregular.xvg')

EDR_DOUBLE = resource_filename(__name__, 'data/double.edr')
EDR_DOUBLE_XVG = resource_filename(__name__, 'data/double.xvg')

EDR_BLOCKS = resource_filename(__name__, 'data/blocks.edr')
EDR_BLOCKS_XVG = resource_filename(__name__, 'data/blocks.xvg')

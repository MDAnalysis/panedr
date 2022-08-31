#-*- coding:utf-8 -*-
# Panedr -- a library to manipulate Gromacs EDR file in python
# Copyright (C) 2016  Jonathan Barnoud
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

# Most of this file is a python rewrite of part of
# `src/gromacs/fileio/enxio.c` from Gromacs 5.1.
# See gromacs.org.

"""
Panedr -- Read Gromacs energy file (EDR) to ``pandas.Dataframe`` in python
==========================================================================

The ``panedr`` library allows users to read and manipulate the content of
Gromacs energy file (.edr files) in python using pandas Dataframes.

This uses the ``pyedr`` library which tries to be in par with Gromacs 5.1.1
when it comes to reading EDR files.

So far, only one function is exposed by the library : the :fun:`edr_to_df`
function that returns a pandas ``DataFrame`` from an EDR file.

.. autofunction:: edr_to_df
"""

from pyedr import read_edr, get_unit_dictionary
import pandas as pd


__all__ = ['edr_to_df', 'get_unit_dictionary']


def edr_to_df(path: str, verbose: bool = False) -> pd.DataFrame:
    """Calls :func:`read_edr` from ``pyedr`` and packs its return values into
    a ``pandas.DataFrame``.

    Parameters
    ----------
    path : str
        path to EDR file to be read
    verbose : bool
        Optionally show verbose output while reading the file
    Returns
    -------
    df: pandas.DataFrame
        :class:`pandas.DataFrame()` object that holds all energy terms found in
        the EDR file.
    """
    all_energies, all_names, times = read_edr(path, verbose=verbose)
    df = pd.DataFrame(all_energies, columns=all_names, index=times)
    return df

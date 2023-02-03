# -*- coding: utf-8 -*-

"""
Tests for panedr
"""

import sys
import pytest
import re
from collections import namedtuple
import pickle

import numpy as np
from numpy.testing import assert_allclose
import pandas
import pyedr
from pyedr.tests.test_edr import read_xvg, redirect_stderr
from pyedr.tests.datafiles import EDR, EDR_XVG, TESTFILE_PARAMS

import panedr


# Constants for XVG parsing
COMMENT_PATTERN = re.compile(r'\s*[@#%&/]')
LEGEND_PATTERN = re.compile(r'@\s+s\d+\s+legend\s+"(.*)"')
NDEC_PATTERN = re.compile(r'[\.eE]')

# Data constants
EDR_Data = namedtuple('EDR_Data', ['df', 'df_units', 'edr_dict', 'edr_units',
                                   'xvgdata', 'xvgtime', 'xvgnames', 'xvgcols',
                                   'xvgprec', 'true_units', 'edrfile',
                                   'xvgfile'])


def check_version_warning(func, edrfile, version):
    if version == panedr.ENX_VERSION:
        return func(edrfile)
    else:
        with pytest.warns(
            UserWarning,
            match=f'enx file_version {version}, '
                  f'implementation version {panedr.ENX_VERSION}'
        ):
            return func(edrfile)


@pytest.fixture(scope='module',
                params=TESTFILE_PARAMS)
def edr(request):
    edrfile, xvgfile, unitfile, version = request.param
    df = check_version_warning(panedr.edr_to_df, edrfile, version)
    df_units = check_version_warning(panedr.get_unit_dictionary,
                                     edrfile, version)
    edr_dict = check_version_warning(pyedr.edr_to_dict, edrfile, version)
    edr_units = check_version_warning(pyedr.get_unit_dictionary,
                                      edrfile, version)
    with open(unitfile, "rb") as f:
        true_units = pickle.load(f)
    xvgdata, xvgnames, xvgprec = read_xvg(xvgfile)
    xvgtime = xvgdata[:, 0]
    xvgdata = xvgdata[:, 1:]
    xvgcols = np.insert(xvgnames, 0, u'Time')
    return EDR_Data(df, df_units, edr_dict, edr_units, xvgdata, xvgtime,
                    xvgnames, xvgcols, xvgprec, true_units, edrfile, xvgfile)


class TestEdrToDf(object):
    """
    Tests for :fun:`panedr.edr_to_df`.
    """

    def test_output_type(self, edr):
        """
        Test that the function returns a pandas DataFrame.
        """
        assert isinstance(edr.df, pandas.DataFrame)

    def test_units(self, edr):
        assert edr.df_units == edr.true_units

    def test_columns(self, edr):
        """
        Test that the column names and order match.
        """
        columns = edr.df.columns.values
        if columns.shape[0] == edr.xvgcols.shape[0]:
            print('These columns differ from the reference '
                  '(displayed as read):')
            print(columns[edr.xvgcols != columns])
            print('The corresponding names displayed as reference:')
            print(edr.xvgcols[edr.xvgcols != columns])
        assert edr.xvgcols.shape == columns.shape, \
               'The number of columns read is unexpected.'
        assert np.all(edr.xvgcols == columns), \
               'At least one column name was misread.'

    def test_times(self, edr):
        """
        Test that the time is read correctly when dt is regular.
        """
        time = edr.df[u'Time'].values
        assert_allclose(edr.xvgtime, time, atol=5e-7)

    def test_content(self, edr):
        """
        Test that the content of the DataFrame is the expected one.
        """
        content = edr.df.iloc[:, 1:].values
        print(edr.xvgdata - content)
        assert_allclose(edr.xvgdata, content, atol=edr.xvgprec/2)

    def test_verbosity(self):
        """
        Make sure the verbose mode does not alter the results.
        """
        with redirect_stderr(sys.stdout):
            df = panedr.edr_to_df(EDR, verbose=True)
        ref_content, _, prec = read_xvg(EDR_XVG)
        content = df.values
        print(ref_content - content)
        assert_allclose(ref_content, content, atol=prec/2)

    def test_edr_dict_to_df_match(self, edr):
        array_df = pandas.DataFrame.from_dict(edr.edr_dict).set_index(
                "Time", drop=False)
        assert array_df.equals(edr.df)

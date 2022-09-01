#-*- coding: utf-8 -*-

"""
Tests for panedr
"""

import sys
import unittest
import pytest
import contextlib
import re
from io import StringIO
from collections import namedtuple
from pathlib import Path
import pickle

import numpy as np
from numpy.testing import assert_allclose
import pandas
import pyedr
from pyedr.tests.test_edr import read_xvg, redirect_stderr
from pyedr.tests.datafiles import (
        EDR, EDR_XVG, EDR_UNITS, EDR_IRREG, EDR_IRREG_XVG,
        EDR_IRREG_UNITS, EDR_DOUBLE, EDR_DOUBLE_XVG, EDR_DOUBLE_UNITS,
        EDR_BLOCKS, EDR_BLOCKS_XVG, EDR_BLOCKS_UNITS
)

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


@pytest.fixture(scope='module',
                params=[(EDR, EDR_XVG, EDR_UNITS),
                        (EDR_IRREG, EDR_IRREG_XVG, EDR_IRREG_UNITS),
                        (EDR_DOUBLE, EDR_DOUBLE_XVG, EDR_DOUBLE_UNITS),
                        (EDR_BLOCKS, EDR_BLOCKS_XVG, EDR_BLOCKS_UNITS),
                        (Path(EDR), EDR_XVG, EDR_UNITS), ])
def edr(request):
    edrfile, xvgfile, unitfile = request.param
    df = panedr.edr_to_df(edrfile)
    df_units = panedr.get_unit_dictionary(edrfile)
    edr_dict = pyedr.edr_to_dict(edrfile)
    edr_units = pyedr.get_unit_dictionary(edrfile)
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
            print('These columns differ from the reference (displayed as read):')
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

    def test_progress(self):
        """
        Test the progress meter displays what is expected.
        """
        output = StringIO()
        with redirect_stderr(output):
            df = panedr.edr_to_df(EDR, verbose=True)
        progress = output.getvalue().split('\n')[0].split('\r')
        print(progress)
        dt = 2000.0
        # We can already iterate on `progress`, but I want to keep the cursor
        # position from one for loop to the other.
        progress_iter = iter(progress)
        assert '' == next(progress_iter)
        self._assert_progress_range(progress_iter, dt, 0, 21, 1)
        self._assert_progress_range(progress_iter, dt, 30, 201, 10)
        self._assert_progress_range(progress_iter, dt, 300, 2001, 100)
        self._assert_progress_range(progress_iter, dt, 3000, 14101, 1000)
        # Check the last line
        print(df.iloc[-1, 0])
        ref_line = 'Last Frame read : 14099, time : 28198000.0 ps'
        last_line = next(progress_iter)
        assert ref_line == last_line
        # Did we leave stderr clean with a nice new line at the end?
        assert output.getvalue().endswith('\n'), \
               'New line missing at the end of output.'

    def _assert_progress_range(self, progress, dt, start, stop, step):
        for frame_idx in range(start, stop, step):
            ref_line = 'Read frame : {},  time : {} ps'.format(frame_idx,
                                                               dt * frame_idx)
            progress_line = next(progress)
            print(frame_idx, progress_line)
            assert ref_line == progress_line

    def test_edr_dict_to_df_match(self, edr):
        array_df = pandas.DataFrame.from_dict(edr.edr_dict).set_index(
                "Time", drop=False)
        assert array_df.equals(edr.df)


if __name__ == '__main__':
    unittest.main()

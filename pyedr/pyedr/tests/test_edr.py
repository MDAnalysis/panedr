#-*- coding: utf-8 -*-

"""
Tests for pyedr
"""
from collections import namedtuple
import contextlib
from io import StringIO
from pathlib import Path
import re
import sys
import unittest
import pickle

import pytest
import numpy as np
from numpy.testing import assert_allclose

import pyedr
from pyedr.tests.datafiles import (
        EDR, EDR_XVG, EDR_UNITS, EDR_IRREG, EDR_IRREG_XVG,
        EDR_IRREG_UNITS, EDR_DOUBLE, EDR_DOUBLE_XVG, EDR_DOUBLE_UNITS,
        EDR_BLOCKS, EDR_BLOCKS_XVG, EDR_BLOCKS_UNITS
)


# Constants for XVG parsing
COMMENT_PATTERN = re.compile(r'\s*[@#%&/]')
LEGEND_PATTERN = re.compile(r'@\s+s\d+\s+legend\s+"(.*)"')
NDEC_PATTERN = re.compile(r'[\.eE]')

# Data constants
EDR_Data = namedtuple('EDR_Data',
                      ['edr_dict', 'edr_units', 'xvgdata', 'xvgtime',
                       'xvgnames', 'xvgcols', 'xvgprec', 'true_units',
                       'edrfile', 'xvgfile'])


@pytest.fixture(scope='module',
                params=[(EDR, EDR_XVG, EDR_UNITS),
                        (EDR_IRREG, EDR_IRREG_XVG, EDR_IRREG_UNITS),
                        (EDR_DOUBLE, EDR_DOUBLE_XVG, EDR_DOUBLE_UNITS),
                        (EDR_BLOCKS, EDR_BLOCKS_XVG, EDR_BLOCKS_UNITS),
                        (Path(EDR), EDR_XVG, EDR_UNITS), ])
def edr(request):
    edrfile, xvgfile, unitfile = request.param
    edr_dict = pyedr.edr_to_dict(edrfile)
    edr_units = pyedr.get_unit_dictionary(edrfile)
    xvgdata, xvgnames, xvgprec = read_xvg(xvgfile)
    with open(unitfile, "rb") as f:
        true_units = pickle.load(f)
    xvgtime = xvgdata[:, 0]
    xvgdata = xvgdata[:, 1:]
    xvgcols = np.insert(xvgnames, 0, u'Time')
    return EDR_Data(edr_dict, edr_units, xvgdata, xvgtime, xvgnames,
                    xvgcols, xvgprec, true_units, edrfile, xvgfile)


class TestEdrToDict(object):
    """
    Tests for :fun:`pyedr.edr_to_dict`.
    """

    def test_output_type(self, edr):
        """
        Test that the function returns a dictionary of ndarrays
        """
        assert isinstance(edr.edr_dict, dict)
        assert isinstance(edr.edr_dict['Time'], np.ndarray)

    def test_units(self, edr):
        assert edr.edr_units == edr.true_units

    def test_columns(self, edr):
        """
        Test that the dictionary names match
        """
        errmsg = "mistmatch in number of colums read"
        assert edr.xvgcols.shape[0] == len(edr.edr_dict), errmsg

        for ref, val in zip(edr.xvgcols, edr.edr_dict.keys()):
            assert ref == val, "mismatching column entries"

    def test_times(self, edr):
        """
        Test that the time is read correctly when dt is regular.
        """
        time = edr.edr_dict['Time']
        assert_allclose(edr.xvgtime, time)

    def test_content(self, edr):
        """
        Test that the content of the DataFrame is the expected one.
        """
        for i, key in enumerate(edr.xvgcols):
            # already tested under `test_times`
            if key != "Time":
                assert_allclose(edr.xvgdata[:, i-1], edr.edr_dict[key],
                                atol=edr.xvgprec/2)

    def test_verbosity(self):
        """
        Make sure the verbose mode does not alter the results.
        """
        with redirect_stderr(sys.stdout):
            edr_dict = pyedr.edr_to_dict(EDR, verbose=True)
        ref_content, _, prec = read_xvg(EDR_XVG)

        for i, key in enumerate(edr_dict.keys()):
            assert_allclose(ref_content[:, i], edr_dict[key],
                            atol=prec/2)

    def test_progress(self):
        """
        Test the progress meter displays what is expected.
        """
        output = StringIO()
        with redirect_stderr(output):
            edr_dict = pyedr.edr_to_dict(EDR, verbose=True)
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


def read_xvg(path):
    """
    Reads XVG file, returning the data, names, and precision.

    The data is returned as a 2D numpy array. Column names are returned as an
    array of string objects. Precision is an integer corresponding to the least
    number of decimal places found, excluding the first (time) column.

    The XVG file type is assumed to be 'xy' or 'nxy'. The function also assumes
    that there is only one serie in the file (no data after // is // is
    present). If more than one serie are present, they will be concatenated if
    the number of column is consistent, is the number of column is not
    consistent among the series, then the function will crash.
    """
    data = []
    names = []
    prec = -1
    with open(path) as infile:
        for line in infile:
            if not re.match(COMMENT_PATTERN, line):
                data.append(line.split())
                precs = [ndec(val) for val in data[-1][1:]]
                if prec == -1:
                    prec = min(precs)
                else:
                    prec = min(prec, *precs)
                continue
            match = re.match(LEGEND_PATTERN, line)
            if match:
                names.append(str(match.groups()[0]))
    if prec <= 0:
        prec = 1.
    else:
        prec = 10**(-prec)

    return (np.array(data, dtype=float),
            np.array(names, dtype=object),
            prec)


def ndec(val):
    """Returns the number of decimal places of a string rep of a float

    """
    try:
        return len(re.split(NDEC_PATTERN, val)[1])
    except IndexError:
        return 0


@contextlib.contextmanager
def redirect_stderr(target):
    """
    Redirect sys.stderr to an other object.

    This function is aimed to be used as a contaxt manager. It is useful
    especially to redirect stderr to stdout as stdout get captured by nose
    while stderr is not. stderr can also get redirected to any other object
    that may act on it, such as a StringIO to inspect its content.
    """
    stderr = sys.stderr
    try:
        sys.stderr = target
        yield
    finally:
        sys.stderr = stderr


if __name__ == '__main__':
    unittest.main()

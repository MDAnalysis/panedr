#-*- coding: utf-8 -*-

"""
Tests for panedr
"""

from __future__ import print_function, division

import six
import os
import sys
import unittest
import pytest
import contextlib
import numpy
import pandas
import panedr
import re

# On python 2, cStringIO is a faster version of StringIO. It may not be
# available on implementations other than Cpython, though. Therefore, we may
# have to fail back on StringIO if cStriongIO is not available.
# On python 3, the StringIO object is not part of the StringIO module anymore.
# It becomes part of the io module.
try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

from collections import namedtuple
try:
    from pathlib import Path
except ImportError:
    # Python 2 requires the pathlib2 backport of pathlib
    from pathlib2 import Path

# Constants for XVG parsing
COMMENT_PATTERN = re.compile(r'\s*[@#%&/]')
LEGEND_PATTERN = re.compile(r'@\s+s\d+\s+legend\s+"(.*)"')
NDEC_PATTERN = re.compile(r'[\.eE]')

# Data constants
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
EDR = os.path.join(DATA_DIR, 'cat.edr')
EDR_XVG = os.path.join(DATA_DIR, 'cat.xvg')  # All EDR fields read with
                                             # ``gmx energy``
EDR_IRREGULAR = os.path.join(DATA_DIR, 'irregular.edr')
EDR_IRREGULAR_XVG = os.path.join(DATA_DIR, 'irregular.xvg')

EDR_DOUBLE = os.path.join(DATA_DIR, 'double.edr')
EDR_DOUBLE_XVG = os.path.join(DATA_DIR, 'double.xvg')

EDR_BLOCKS = os.path.join(DATA_DIR, 'blocks.edr')
EDR_BLOCKS_XVG = os.path.join(DATA_DIR, 'blocks.xvg')

EDR_Data = namedtuple('EDR_Data', ['df', 'xvgdata', 'xvgtime', 'xvgnames',
                                   'xvgprec', 'edrfile', 'xvgfile'])

@pytest.fixture(scope='module',
                params=[(EDR, EDR_XVG),
                        (EDR_IRREGULAR, EDR_IRREGULAR_XVG),
                        (EDR_DOUBLE, EDR_DOUBLE_XVG),
                        (EDR_BLOCKS, EDR_BLOCKS_XVG),
                        (Path(EDR), EDR_XVG),
                       ])
def edr(request):
    edrfile, xvgfile = request.param
    df = panedr.edr_to_df(edrfile)
    xvgdata, xvgnames, xvgprec = read_xvg(xvgfile)
    xvgtime = xvgdata[:, 0]
    xvgdata = xvgdata[:, 1:]
    return EDR_Data(df, xvgdata, xvgtime, xvgnames, xvgprec, edrfile, xvgfile)
    

class TestEdrToDf(object):
    """
    Tests for :fun:`panedr.edr_to_df`.
    """
    def test_output_type(self, edr):
        """
        Test that the function returns a pandas DataFrame.
        """
        assert isinstance(edr.df, pandas.DataFrame)

    def test_columns(self, edr):
        """
        Test that the column names and order match.
        """
        ref_columns = numpy.insert(edr.xvgnames, 0, u'Time')
        columns = edr.df.columns.values
        if columns.shape[0] == ref_columns.shape[0]:
            print('These columns differ from the reference (displayed as read):')
            print(columns[ref_columns != columns])
            print('The corresponding names displayed as reference:')
            print(ref_columns[ref_columns != columns])
        assert ref_columns.shape == columns.shape, \
               'The number of columns read is unexpected.'
        assert numpy.all(ref_columns == columns), \
               'At least one column name was misread.'

    def test_times(self, edr):
        """
        Test that the time is read correctly when dt is regular.
        """
        time = edr.df[u'Time'].values
        assert numpy.allclose(edr.xvgtime, time, atol=5e-7)

    def test_content(self, edr):
        """
        Test that the content of the DataFrame is the expected one.
        """
        content = edr.df.iloc[:, 1:].values
        print(edr.xvgdata - content)
        assert numpy.allclose(edr.xvgdata, content, atol=edr.xvgprec/2)

    def test_verbosity(self):
        """
        Make sure the verbose mode does not alter the results.
        """
        with redirect_stderr(sys.stdout):
            df = panedr.edr_to_df(EDR, verbose=True)
        ref_content, _, prec = read_xvg(EDR_XVG)
        content = df.values
        print(ref_content - content)
        assert numpy.allclose(ref_content, content, atol=prec/2)

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
                names.append(six.text_type(match.groups()[0]))
    if prec <= 0:
        prec = 1.
    else:
        prec = 10**(-prec)

    return (numpy.array(data, dtype=float),
            numpy.array(names, dtype=object),
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

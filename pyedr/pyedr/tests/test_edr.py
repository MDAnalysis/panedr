# -*- coding: utf-8 -*-

"""
Tests for pyedr
"""
from collections import namedtuple
import contextlib
import re
import sys
import pickle

import pytest
import numpy as np
from numpy.testing import assert_allclose

import pyedr
from pyedr.tests.datafiles import EDR, EDR_XVG, TESTFILE_PARAMS


# Constants for XVG parsing
COMMENT_PATTERN = re.compile(r'\s*[@#%&/]')
LEGEND_PATTERN = re.compile(r'@\s+s\d+\s+legend\s+"(.*)"')
NDEC_PATTERN = re.compile(r'[\.eE]')

# Data constants
EDR_Data = namedtuple('EDR_Data',
                      ['edr_dict', 'edr_units', 'xvgdata', 'xvgtime',
                       'xvgnames', 'xvgcols', 'xvgprec', 'true_units',
                       'edrfile', 'xvgfile'])


def check_version_warning(func, edrfile, version):
    if version == pyedr.ENX_VERSION:
        return func(edrfile)
    else:
        with pytest.warns(
            UserWarning,
            match=f'enx file_version {version}, '
                  f'implementation version {pyedr.ENX_VERSION}'
        ):
            return func(edrfile)


@pytest.fixture(scope='module',
                params=TESTFILE_PARAMS)
def edr(request):
    edrfile, xvgfile, unitfile, version = request.param
    edr_dict = check_version_warning(pyedr.edr_to_dict, edrfile, version)
    edr_units = check_version_warning(pyedr.get_unit_dictionary,
                                      edrfile, version)
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
                                atol=edr.xvgprec)

    def test_verbosity(self):
        """
        Make sure the verbose mode does not alter the results.
        """
        with redirect_stderr(sys.stdout):
            edr_dict = pyedr.edr_to_dict(EDR, verbose=True)
        ref_content, _, prec = read_xvg(EDR_XVG)

        for i, key in enumerate(edr_dict.keys()):
            assert_allclose(ref_content[:, i], edr_dict[key],
                            atol=prec)


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

    This function is aimed to be used as a context manager. It is useful
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

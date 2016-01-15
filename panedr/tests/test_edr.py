#-*- coding: utf-8 -*-

"""
Tests for panedr
"""

from __future__ import print_function, division

import os
import unittest
import numpy
import pandas
import panedr

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
EDR = os.path.join(DATA_DIR, 'cat.edr')
EDR_XVG = os.path.join(DATA_DIR, 'cat.xvg')  # A EDR fields read with
                                             # ``gmx energy``
EDR_IRREGULAR = os.path.join(DATA_DIR, 'irregular.edr')
EDR_IRREGULAR_XVG = os.path.join(DATA_DIR, 'irregular.xvg')


class TestEdrToDf(unittest.TestCase):
    """
    Tests for :fun:`panedr.edr_to_df`.
    """
    def test_output_type(self):
        """
        Test that the function returns a pandas DataFrame.
        """
        df = panedr.edr_to_df(EDR)
        self.assertIsInstance(df, pandas.DataFrame)

    def test_columns(self):
        """
        Test that the column names and order match.
        """
        df = panedr.edr_to_df(EDR)
        ref_columns = numpy.array([u'Time', u'Bond', u'G96Angle',
                                   u'Improper Dih.', u'LJ (SR)',
                                   u'Coulomb (SR)', u'Potential',
                                   u'Kinetic En.', u'Total Energy',
                                   u'Temperature', u'Pressure',
                                   u'Constr. rmsd', u'Box-X', u'Box-Y',
                                   u'Box-Z', u'Volume', u'Density', u'pV',
                                   u'Enthalpy', u'Vir-XX', u'Vir-XY',
                                   u'Vir-XZ', u'Vir-YX', u'Vir-YY', u'Vir-YZ',
                                   u'Vir-ZX', u'Vir-ZY', u'Vir-ZZ', u'Pres-XX',
                                   u'Pres-XY', u'Pres-XZ', u'Pres-YX',
                                   u'Pres-YY', u'Pres-YZ', u'Pres-ZX',
                                   u'Pres-ZY', u'Pres-ZZ', u'#Surf*SurfTen',
                                   u'Box-Vel-XX', u'Box-Vel-YY', u'Box-Vel-ZZ',
                                   u'Mu-X', u'Mu-Y', u'Mu-Z',
                                   u'Coul-SR:water-water',
                                   u'LJ-SR:water-water', u'Coul-SR:water-DPPC',
                                   u'LJ-SR:water-DPPC', u'Coul-SR:water-DUPC',
                                   u'LJ-SR:water-DUPC', u'Coul-SR:water-CHOL',
                                   u'LJ-SR:water-CHOL', u'Coul-SR:water-OCO',
                                   u'LJ-SR:water-OCO', u'Coul-SR:DPPC-DPPC',
                                   u'LJ-SR:DPPC-DPPC', u'Coul-SR:DPPC-DUPC',
                                   u'LJ-SR:DPPC-DUPC', u'Coul-SR:DPPC-CHOL',
                                   u'LJ-SR:DPPC-CHOL', u'Coul-SR:DPPC-OCO',
                                   u'LJ-SR:DPPC-OCO', u'Coul-SR:DUPC-DUPC',
                                   u'LJ-SR:DUPC-DUPC', u'Coul-SR:DUPC-CHOL',
                                   u'LJ-SR:DUPC-CHOL', u'Coul-SR:DUPC-OCO',
                                   u'LJ-SR:DUPC-OCO', u'Coul-SR:CHOL-CHOL',
                                   u'LJ-SR:CHOL-CHOL', u'Coul-SR:CHOL-OCO',
                                   u'LJ-SR:CHOL-OCO', u'Coul-SR:OCO-OCO',
                                   u'LJ-SR:OCO-OCO', u'T-non_water',
                                   u'T-water', u'Lamb-non_water',
                                   u'Lamb-water'], dtype='object')
        columns = df.columns.values
        if columns.shape[0] == ref_columns.shape[0]:
            print('These columns differ from the reference (displayed as read):')
            print(columns[ref_columns != columns])
            print('The corresponding names displayed as reference:')
            print(ref_columns[ref_columns != columns])
        self.assertTrue(ref_columns.shape == columns.shape,
                        'The number of column read is unexpected.')
        self.assertTrue(numpy.all(ref_columns == columns),
                        'At least one column name was misread.')

    def test_times(self):
        """
        Test that the time is read correctly when dt is regular.
        """
        df = panedr.edr_to_df(EDR)
        xvg = read_xvg(EDR_XVG)
        ref_time = xvg[:, 0]
        time = df[u'Time'].as_matrix()
        self.assertTrue(numpy.allclose(ref_time, time, atol=5e-7))

    def test_times_irregular(self):
        """
        Test that the time is read correctly when dt has irregularities.
        """
        df = panedr.edr_to_df(EDR_IRREGULAR)
        xvg = read_xvg(EDR_IRREGULAR_XVG)
        ref_time = xvg[:, 0]
        time = df[u'Time'].as_matrix()
        self.assertTrue(numpy.allclose(ref_time, time, atol=5e-7))

    def test_content(self):
        """
        Test that the content of the DataFrame is the expected one.
        """
        df = panedr.edr_to_df(EDR)
        xvg = read_xvg(EDR_XVG)
        ref_content = xvg[:, 1:]  # The time column is tested separately
        content = df.iloc[:, 1:].as_matrix()
        print(ref_content - content)
        self.assertTrue(numpy.allclose(ref_content, content, atol=5e-7))

    def test_verbose(self):
        """
        Make sure the verbose mode does not alter the results.
        """
        df = panedr.edr_to_df(EDR, verbose=True)
        ref_content = read_xvg(EDR_XVG)
        content = df.as_matrix()
        print(ref_content - content)
        self.assertTrue(numpy.allclose(ref_content, content, atol=5e-7))


def read_xvg(path):
    """
    Read a XVG file and returns a 2D numpy array.

    The XVG file type is assumed to be 'xy' or 'nxy'. The function also assumes
    that there is only one serie in the file (no data after // is // is
    present). If more than one serie are present, they will be concatenated is
    the number of column is consitent, is the number of column is not
    consistent among the series, then the function will crash.
    """
    with open(path) as infile:
         data = numpy.array([line.split() for line in infile
                             if not line[0] in '@#%&/'],
                            dtype=float)
    return data


if __name__ == '__main__':
    unittest.main()

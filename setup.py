#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.rst') as infile:
    readme = infile.read()

with open('panedr/VERSION') as infile:
    version = infile.read().strip()

setup(name='panedr',
      version=version,
      description='Read and manipulate Gromacs energy files',
      long_description=readme,
      url='https://github.com/jbarnoud/panedr',
      author='Jonathan Barnoud',
      author_email='jonathan@barnoud.net',
      license='LGPL',
      classifiers=['Development Status :: 4 - Beta',
                   # Indicate who your project is intended for
                   'Intended Audience :: Developers',
                   'Topic :: Scientific/Engineering :: Bio-Informatics',
                   'Topic :: Scientific/Engineering :: Chemistry',
                   'Topic :: Scientific/Engineering :: Physics',

                   'License :: OSI Approved :: '
                     'GNU Lesser General Public License v2 or later (LGPLv2+)',

                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',

                   'Operating System :: OS Independent',
                   ],
      packages=find_packages(),
      install_requires=['pandas'],
      test_suite='panedr.tests',
      tests_require=['nose'],
      package_data={'panedr': ['VERSION', 'tests/test*.py', 'tests/data/*']}
      )

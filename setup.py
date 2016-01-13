#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.md') as infile:
    readme = infile.read()

setup(name='panedr',
      version='0.1',
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

                   'License :: OSI Approved ::  LGPL',

                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   ],
      packages=find_packages(),
      install_requires=['pandas'],
      test_suite='panedr.tests',
      tests_require=['nose'],
      package_data={'panedr': ['tests/test*.py', 'tests/data/*']}
      )

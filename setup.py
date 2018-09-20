#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.rst') as infile:
    readme = infile.read()

with open('panedr/VERSION') as infile:
    version = infile.read().strip()

tests_require = ['pytest', 'six']

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
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',

                   'Operating System :: OS Independent',
                   ],
      packages=find_packages(),
      install_requires=['pandas'],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      package_data={'panedr': ['VERSION', ]},
      python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
      )

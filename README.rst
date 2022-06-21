Panedr
======

|Build Status| |cov|

Panedr reads a `Gromacs EDR`_ binary energy XDR file and returns its content 
as a pandas_ dataframe. The library exposes one function—the ``edr_to_df``
function—that gets the path to an EDR file and returns a pandas
dataframe.

``panedr`` is compatible with Python 3.6 and greater.

Example
-------

.. code:: python

    import panedr

    # Read the EDR file
    path = 'ener.edr'
    df = panedr.edr_to_df(path)

    # The `verbose` optional parameter can be set to True to display the
    # progress on stderr
    df = panedr.edr_to_df(path, verbose=True)

    # Get the average pressure after the first 10 ns
    pressure_avg = df[u'Pressure'][df[u'Time'] > 10000].mean()

Install
-------

Install the package with ``pip``:

.. code:: bash

    pip install panedr

If you are using `conda`_ and `conda-forge`_, you can install with

.. code:: bash

    conda install -c conda-forge panedr

Tests
-----

The ``panedr`` repository contains a series of tests. If you downloaded or
cloned the code from the repository, you can run the tests. To do so,
install pytest`_, and, in the directory of the
panedr source code, run:

.. code:: bash

    pytest -v tests

License
-------

Panedr translate in python part of the source code of Gromacs.
Therefore, Panedr is distributed under the same GNU Lesser General
Public License version 2.1 as Gromacs.

    Panedr — a library to manipulate Gromacs EDR file in python

    Copyright (C) 2016 Jonathan Barnoud

    This library is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as
    published by the Free Software Foundation; either version 2.1 of the
    License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
    02110-1301 USA

.. |Build Status| image:: https://github.com/MDAnalysis/panedr/actions/workflows/gh-ci.yaml/badge.svg
   :alt: Github Actions Build Status
   :target: https://github.com/MDAnalysis/panedr/actions/workflows/gh-ci.yaml
   
.. |cov|   image:: https://codecov.io/gh/MDAnalysis/panedr/branch/master/graph/badge.svg
   :alt: Coverage Status
   :target: https://codecov.io/gh/MDAnalysis/panedr

.. _`Gromacs EDR`: https://manual.gromacs.org/documentation/current/reference-manual/file-formats.html#edr
.. _pandas: https://pandas.pydata.org/
.. _conda: https://docs.conda.io
.. _`conda-forge`: https://conda-forge.org/
.. _pytest: https://docs.pytest.org/

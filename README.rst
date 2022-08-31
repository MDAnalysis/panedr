Pyedr and Panedr
================

|Build Status| |cov|

This repository hosts the source files for both the Pyedr and Panedr packages.

``pyedr`` and ``panedr`` are compatible with Python 3.6 and greater.

Pyedr
-----

Pyedr provides a means of reading a `Gromacs EDR`_ binary XDR file and
return its contents as a dictionary of `numpy`_ arrays. Pyedr exposes
the following functions:

- ``edr_to_dict``: returns a dictionary of NumPy arrays keyed by the energy
  type from a given path to an EDR file.
- ``read_edr``: parses an EDR file and returns the energy terms
  in a nested list
- ``get_unit_dictionary``: Returns a dictionary that holds the units of each
  energy term found in the EDR file.


Panedr
------

Panedr uses the Pyedr library to read a `Gromacs EDR`_ binary energy XDR file
and returns its contents as a pandas_ dataframe. Panedr exposes the
following functions:

- ``edr_to_df``: which gets the path to an EDR file and returns a
  pandas DataFrame.
- ``get_unit_dictionary``: Returns a dictionary that holds the units of each
  energy term found in the EDR file.


Example
-------

Using ``pyedr``:


.. code:: python

    import pyedr

    # Read the EDR file
    path = 'ener.edr'
    dic = pyedr.edr_to_dict(path)

    # The `verbose` optional parameter can be set to True to display the
    # progress on stderr
    dic = pyedr.edr_to_dict(path, verbose=True)

    # Get the average pressure after the first 10 ns
    pressure_avg = dic['Pressure'][dic['Time'] > 10000].mean()

    # Get the units of the EDR entries
    unit_dict = pyedr.get_unit_dictionary(path)
    unit_dict["Temperature"]  # returns "K"


Using ``panedr``:


.. code:: python

    import panedr

    # Read the EDR file
    path = 'ener.edr'
    df = panedr.edr_to_df(path)

    # The `verbose` optional parameter can be set to True to display the
    # progress on stderr
    df = panedr.edr_to_df(path, verbose=True)

    # Get the average pressure after the first 10 ns
    pressure_avg = df['Pressure'][df['Time'] > 10000].mean()

    # Get the units of the EDR entries
    unit_dict = panedr.get_unit_dictionary(path)
    unit_dict["Temperature"]  # returns "K"


Install
-------

You can install ``pyedr`` and ``panedr`` using ``pip``:

.. code:: bash

    pip install pyedr

    # installing panedr automatically installs pyedr
    pip install panedr


If you are using `conda`_ and `conda-forge`_, you can install with:

.. code:: bash

    conda install -c conda-forge pyedr

    # install panedr automatically installs pyedr
    conda install -c conda-forge panedr


Tests
-----

The ``pyedr`` and ``panedr`` repositories contains a series of tests.
If you downloaded or cloned the code from the repository, you can run
the tests. To do so, install `pytest`_, and, in the directory of the
panedr source code, run:

For ``pyedr``:


.. code:: bash

    pytest -v pyedr/pyedr/tests


For ``panedr``:


.. code:: bash

    pytest -v panedr/panedr/tests


License
-------

Pyedr and Panedr translate part of the source code of Gromacs into Python.
Therefore, Panedr is distributed under the same GNU Lesser General
Public License version 2.1 as Gromacs. See the `license`_ for more details.


.. |Build Status| image:: https://github.com/MDAnalysis/panedr/actions/workflows/gh-ci.yaml/badge.svg
   :alt: Github Actions Build Status
   :target: https://github.com/MDAnalysis/panedr/actions/workflows/gh-ci.yaml

.. |cov|   image:: https://codecov.io/gh/MDAnalysis/panedr/branch/master/graph/badge.svg
   :alt: Coverage Status
   :target: https://codecov.io/gh/MDAnalysis/panedr

.. _`Gromacs EDR`: https://manual.gromacs.org/documentation/current/reference-manual/file-formats.html#edr
.. _numpy: https://numpy.org/
.. _pandas: https://pandas.pydata.org/
.. _conda: https://docs.conda.io
.. _`conda-forge`: https://conda-forge.org/
.. _pytest: https://docs.pytest.org/
.. _license: https://github.com/MDAnalysis/panedr/blob/master/LICENSE.txt

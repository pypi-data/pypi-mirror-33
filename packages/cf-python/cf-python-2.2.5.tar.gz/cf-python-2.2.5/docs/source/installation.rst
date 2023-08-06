.. currentmodule:: cf
.. default-role:: obj

.. highlight:: bash

Installation
============

Dependencies
------------

See `<https://bitbucket.org/cfpython/cf-python/overview>`_ for the
current list of dependencies.

Install with conda
------------------

To install cf-python download and install Anaconda Python 2.7. On the
command line type

::

   conda install -c ncas -c conda-forge cf-plot
   conda install -c conda-forge -c nesii netcdf-fortran=4.4.4 mpich esmpy

The first line installs cf-python. The second installs esmpy, together
with the netcdf-fortran and mpich requirements, which cf-python uses
for regriding data.

Install with pip
----------------

cf-python is available from the python package index
(`<https://pypi.python.org/pypi/cf-python>`_).

::

   $ pip install cf-python

Install from source
-------------------

Download the cf package from
`<https://pypi.python.org/pypi/cf-python>`_

Unpack the library (replacing <version> with the approrpriate release,
e.g. ``2.2.4``)::

   $ tar zxvf cf-python-<version>.tar.gz
   $ cd cf-python-<version>

To install the cf package to a central location::

   $ python setup.py install

To install the cf package locally to the user in the default location
(often within ``~/.local``)::

   $ python setup.py install --user

To install the cf package in the <directory> of your choice::

   $ python setup.py install --home=<directory>


Issues
------

Please raise any questions or problems at
`<https://bitbucket.org/cfpython/cf-python/issues>`_

==============
FluidSim_ocean
==============

|release| |docs| |coverage|

.. |release| image:: https://badge.fury.io/py/fluidsim_ocean.svg
   :target: https://pypi.python.org/pypi/fluidsim_ocean/
   :alt: Latest version

.. |docs| image:: https://readthedocs.org/projects/fluidsim_ocean/badge/?version=latest
   :target: http://fluidsim_ocean.readthedocs.org
   :alt: Documentation status

.. |coverage| image:: https://codecov.io/bb/fluiddyn/fluidsim_ocean/branch/default/graph/badge.svg
   :target: https://codecov.io/bb/fluiddyn/fluidsim_ocean
   :alt: Code coverage

The Python package Fluidsim_ocean provides solvers useful for studying the oceanic
dynamics implemented using the CFD framework `fluidsim
<http://fluidsim.readthedocs.org>`_.

Installation
------------

For simple setup, ``pip install fluidsim_ocean`` should work.

If you care about performance, first install `fluidsim
<http://fluidsim.readthedocs.org>`_ and then, get the source code of
fluidsim_ocean from `Bitbucket <https://bitbucket.org/fluiddyn/fluidsim_ocean>`__
and install with::

  python setup.py develop

Tests
-----

From the root directory::

  make tests
  make tests_mpi

Or, from the root directory or from any of the "test" directories::

  python -m unittest discover

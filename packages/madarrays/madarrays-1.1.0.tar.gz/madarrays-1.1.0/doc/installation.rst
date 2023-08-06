Installation
############

``madarrays`` requires the following packages:

* `python >= 3.5 <https://wiki.python.org/moin/BeginnersGuide/Download>`_
* `numpy >= 1.13 <http://www.numpy.org>`_
* `scipy >= 0.19 <https://www.scipy.org/scipylib/index.html>`_
* `matplotlib >= 2.1 <http://matplotlib.org/>`_
* `simpleaudio >= 1.0 <https://github.com/hamiltron/py-simple-audio>`_
* `resampy >= 0.2 <https://github.com/bmcfee/resampy>`_

Make sure your Python environment is properly configured. It is recommended to
install ``madarrays`` in a virtual environment.

Release version
---------------

First, make sure you have the latest version of pip (the Python package
manager) installed. If you do not, refer to the `Pip documentation
<https://pip.pypa.io/en/stable/installing/>`_ and install ``pip`` first.

Install the current release with ``pip``::

    pip install madarrays

To upgrade to a newer release use the ``--upgrade`` flag::

    pip install --upgrade madarrays

If you do not have permission to install software systemwide, you can install
into your user directory using the ``--user`` flag::

    pip install --user madarrays

Alternatively, you can manually download ``madarrays`` from its `GitLab project
<https://gitlab.lis-lab.fr/skmad-suite/madarrays>`_  or `PyPI
<https://pypi.python.org/pypi/madarrays>`_.  To install one of these versions,
unpack it and run the following from the top-level source directory using the
Terminal::

    pip install .

Development version
-------------------

If you have `Git <https://git-scm.com/>`_ installed on your system, it is also
possible to install the development version of ``madarrays``.

Before installing the development version, you may need to uninstall the
standard version of ``madarrays`` using ``pip``::

    pip uninstall madarrays

Clone the Git repository::

    git clone git@gitlab.lis-lab.fr:skmad-suite/madarrays.git
    cd madarrays

You may also need to install required packages::

    pip install -r requirements/defaults.txt

Then execute ``pip`` with flag ``-e`` to follow the development branch::

    pip install -e .

To update ``madarrays`` at any time, in the same directory do::

    git pull

To run unitary tests, first install required packages::

    pip install -r requirements/dev.txt

and execute ``pytest``::

    pytest


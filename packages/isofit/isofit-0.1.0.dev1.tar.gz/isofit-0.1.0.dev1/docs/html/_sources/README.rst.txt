Imaging Spectrometer Optimal FITting (ISOFIT)
=============================================

This codebase contains a set of routines and utilities for fitting surface,
atmosphere and instrument models to imaging spectrometer data.  It is
written primarily in Python, with JSON format configuration files and some
dependencies on widely-available numerical and scientific libraries such as
scipy, scikit-learn, and numba.  It is designed for maximum flexibility, so
that users can swap in and evaluate model components based on different
radiative transfer models (RTMs) and various statistical descriptions of
surface, instrument, and atmosphere.  It can run on individual radiance
spectra in text format, or imaging spectrometer data cubes.

The subdirectories contain:

* data/      - shared data files
* docs/      - documentation
* examples/  - a series of example runs packaged with input data and sample configuration files.
* isofit/    - the main Python codebase, with the top-level program isofit.py.
* utils/     - general purpose utilities and routines.

Installation Instructions
-------------------------

The latest release is always hosted on `PyPI <https://pypi.python.org/pypi/isofit>`_,
so if you have `pip` installed, you can install ISOFIT from the command line with

.. code::

    pip install isofit

The code repository, development branches, and user community are found at
`GitHub <https://github.com/davidraythompson/isofit>`_

If you wish, you can simply download or clone the git repository
and run ISOFIT directly on an example. No explicit installation is required; simply
make sure the utils/ and isofit/ subdirectories are in your Python path.

Quick Start
-----------

This quick start presumes that you are using the MODTRAN 6.0
radiative transfer model.  Other open-source options including LibRadTran and
neural network emulators will also be integrated in the future, however, for the current release MODTRAN 6.0 is required.

1. Configure your environment with the variables ISOFIT_BASE pointing to the base checkout directory of ISOFIT, and also MODTRAN_DIR pointing to the base MODTRAN 6.0 directory.

2. Run the following code

.. code::

    cd examples/20171108_Pasadena
    ./run_example.sh

3. This will build surface models and run the retrieval. The default example uses a lookup table approximation, and the code should recognize that the tables do not currently exist.  It will call MODTRAN to rebuild them, which will take a few minutes.

4. Look for output data in examples/20171108_Pasadena/output/.

ISOFIT Dependencies
-------------------

The ISOFIT dependencies should automatically get installed if you use the "pip install isofit" method.  However, if you've cloned the repo and need to get the libraries separately, then run the following:

.. code::

  python3 -m pip install scipy
  python3 -m pip install numba
  python3 -m pip install matplotlib
  python3 -m pip install scikit-learn
  python3 -m pip install spectral


Additional Installation Info for Mac OSX
------------------------------------------

1. Install the command-line compiler

.. code::

  xcode-select --install

2. Download the python3 installer from https://www.python.org/downloads/mac-osx/

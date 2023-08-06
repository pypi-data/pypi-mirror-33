###########################
:mod:`pyteuf` documentation
###########################

Overview
========
:mod:`pyteuf` is a package for time-frequency analysis/synthesis with possibly
missing data in Python.

:mod:`pyteuf` provides:

* a time-frequency 2D data structure :class:`TfData <pyteuf.tf_data.TfData>` to
  manipulate time-frequency representations, either complex (STFT, etc.) or
  real (spectrograms, etc.) in which some coefficients may be missing
  (missing amplitude, missing phase, or both).
* a class :class:`Stft <pyteuf.tf_transforms.Stft>` and a class
  :class:`Istft <pyteuf.tf_transforms.Istft>`, which are an interface to
  :mod:`ltfatpy` in order to facilitate the use of direct and inverse
  short-time Fourier transforms.


Documentation
=============

.. only:: html

    :Release: |version|
    :Date: |today|

.. toctree::
    :maxdepth: 1

    installation
    references
    tutorials
    credits


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`





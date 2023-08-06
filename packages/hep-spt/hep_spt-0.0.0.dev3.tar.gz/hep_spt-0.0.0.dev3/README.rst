=======
hep_spt
=======

.. image:: https://img.shields.io/travis/mramospe/hep_spt.svg
   :target: https://travis-ci.org/mramospe/hep_spt

.. image:: https://img.shields.io/badge/documentation-link-blue.svg
   :target: https://mramospe.github.io/hep_spt/

.. inclusion-marker-do-not-remove

The **High Energy Physics Statistics and Plotting Tools** package provides tools to work in **High Energy Physics** using general python packages.

Main points
===========

  * Functions needed on day-to-day work, like calculating errors, residuals, etc.
  * Classes to create adaptive binned histograms, and some functions to represent them using `matplotlib <https://matplotlib.org/>`_.
  * Statistical functions to work with Bayesian/Frequentist approaches.
  * Utilities to handle poissonian and/or weighted histograms.
  * Simple classes to work with the CLs method.
  * A set of `matplotlib <https://matplotlib.org/>`_ styles.

Considerations:
===============

  * Inputs passed to the functions and classes are usually preferred as `numpy.ndarray <https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.ndarray.html>`_ objects.
  * Plotting functions and classes are designed to work with `matplotlib <https://matplotlib.org/>`_.
  * Statistical tools are built on top of the standard `scipy <https://scipy.org/>`_ package.

Installation:
=============

This package is available on `PyPi <https://pypi.org/>`_, so simply type

.. code-block:: bash

   pip install hep-spt

to install the package in your current python environment.
Since this package uses the Numpy C API, it is necessary to have Numpy already installed.
If you attempt to install "hep_spt" with no installation of Numpy, an error will be raised.
To use the **latest development version**, clone the repository and install with `pip`:

.. code-block:: bash

   git clone https://github.com/mramospe/hep_spt.git
   pip install hep_spt

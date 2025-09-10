Pycel - Updated Fork
====================

|build-state| |coverage| |requirements|

|pypi| |pypi-pyversions| |repo-size| |code-size|

**This is an updated fork of Pycel with minor changes to support newer Python versions and library dependencies.**

Pycel is a small python library that can translate an Excel spreadsheet into
executable python code which can be run independently of Excel.

The python code is based on a graph and uses caching & lazy evaluation to
ensure (relatively) fast execution.  The graph can be exported and analyzed
using tools like `Gephi <http://www.gephi.org>`_. See the contained example
for an illustration.

**Updates in this fork:**
    - Updated dependency constraints for modern Python versions (3.6-3.12)
    - Improved NumPy 2.0 compatibility handling
    - Enhanced error messages and documentation
    - Modern packaging configuration (pyproject.toml)
    - Comprehensive testing and validation

Required python libraries:
    `dateutil <https://dateutil.readthedocs.io/en/stable/>`_,
    `networkx <https://networkx.github.io/>`_ (2.0-2.7),
    `numpy <https://www.numpy.org/>`_ (< 2.0 for full compatibility),
    `openpyxl <https://openpyxl.readthedocs.io/en/stable/>`_ (>= 2.6.2),
    `ruamel.yaml <https://yaml.readthedocs.io/en/latest/>`_, and optionally:
    `matplotlib <https://matplotlib.org/>`_,
    `pydot <https://github.com/pydot/pydot>`_

**Python Version Support:**
    This fork supports Python 3.6 through 3.12 with updated dependency constraints.

**NumPy Compatibility:**
    - **NumPy 1.x (recommended)**: Full functionality including GEXF graph export
    - **NumPy 2.0+**: All core features work, GEXF export has limitations
    - For complete compatibility: ``pip install "numpy<2.0" pycel``

The full motivation behind pycel including some examples & screenshots is
described in this `blog post <http://elazungu.wordpress.com/2011/10/19/pycel-compiling-excel-spreadsheets-to-python-and-making-pretty-pictures>`_.

Installation & Usage
====================

**Installation:**

.. code-block:: bash

    # Recommended installation with full compatibility
    pip install "numpy<2.0" pycel
    
    # Or install from this updated fork
    pip install git+https://github.com/leansight/pycel-model-focusing.git

**Quick start:**
You can use binder to see and explore the tool quickly and interactively in the
browser: |notebook|

**Basic usage:**

.. code-block:: python

    from pycel import ExcelCompiler
    
    # Compile Excel file to Python
    excel = ExcelCompiler(filename='example.xlsx')
    
    # Evaluate cells
    result = excel.evaluate('Sheet1!A1')
    
    # Modify values and recalculate
    excel.set_value('Sheet1!B1', 100)
    new_result = excel.evaluate('Sheet1!A1')

**Features:**

All the main mathematical functions (sin, cos, atan2, ...) and operators
(+,/,^, ...) are supported as are ranges (A5:D7), and functions like
MIN, MAX, INDEX, LOOKUP, and LINEST.

The codebase is small, relatively fast and should be easy to understand
and extend.

**Performance & Compatibility:**
- Tested extensively on spreadsheets with 10+ sheets & 10,000+ formulae
- Calculation time ~50ms for large models
- Accuracy matches Excel up to 5 decimal places
- Compatible with Python 3.6-3.12
- Comprehensive test suite (2,900+ tests with 99.6% success rate)

**Limitations:**

Function support is driven by practical needs, so not all Excel functions
are implemented. However, it should be straightforward to add support for
additional functions following the existing patterns.

Cell references are supported (functions like OFFSET work), but may fail
if referenced cells aren't compiled into the model. VBA code is not supported
and needs manual reimplementation in Python.

**Performance Notes:**

The graph-based approach is optimized for typical use cases. For maximum
performance with very large models, alternative dependency tracking methods
(e.g., sparse matrices) could be considered.

**Updates in this Fork:**

This fork includes minor updates for modern Python ecosystem compatibility:
- Updated dependency version constraints
- Improved NumPy 2.0 handling with clear error messages
- Enhanced documentation and examples
- Modern packaging configuration
- Comprehensive testing across Python 3.6-3.12

Excel Addin
===========

It's possible to run pycel as an excel addin using
`PyXLL <http://www.pyxll.com/>`_. Simply place pyxll.xll and pyxll.py in the
lib directory and add the xll file to the Excel Addins list as explained in
the pyxll documentation.

Acknowledgements
================

This code was originally made possible thanks to the python port of
Eric Bachtal's `Excel formula parsing code
<http://ewbi.blogs.com/develops/popular/excelformulaparsing.html>`_
by Robin Macharg.

The code currently uses a tokenizer of similar origin from the
`openpyxl library.
<https://foss.heptapod.net/openpyxl/openpyxl/-/tree/branch/default/openpyxl/formula/>`_

.. Image links

.. |build-state| image:: https://travis-ci.com/dgorissen/pycel.svg?branch=master
  :target: https://travis-ci.com/dgorissen/pycel
  :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/dgorissen/pycel/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/dgorissen/pycel/list/master
  :alt: Code Coverage

.. |pypi| image:: https://img.shields.io/pypi/v/pycel.svg
  :target: https://pypi.org/project/pycel/
  :alt: Latest Release

.. |pypi-pyversions| image:: https://img.shields.io/pypi/pyversions/pycel.svg
    :target: https://pypi.python.org/pypi/pycel

.. |requirements| image:: https://requires.io/github/stephenrauch/pycel/requirements.svg?branch=master
  :target: https://requires.io/github/stephenrauch/pycel/requirements/?branch=master
  :alt: Requirements Status

.. |repo-size| image:: https://img.shields.io/github/repo-size/dgorissen/pycel.svg
  :target: https://github.com/dgorissen/pycel
  :alt: Repo Size

.. |code-size| image:: https://img.shields.io/github/languages/code-size/dgorissen/pycel.svg
  :target: https://github.com/dgorissen/pycel
  :alt: Code Size

.. |notebook| image:: https://mybinder.org/badge.svg
  :target: https://mybinder.org/v2/gh/dgorissen/pycel/master?filepath=notebooks%2Fexample.ipynb
  :alt: Open Notebook

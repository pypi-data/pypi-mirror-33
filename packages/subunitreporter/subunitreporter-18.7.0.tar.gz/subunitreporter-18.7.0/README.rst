subunitreporter
===============

.. image:: http://img.shields.io/pypi/v/subunitreporter.svg
   :target: https://pypi.python.org/pypi/subunitreporter
   :alt: PyPI Package

What is this?
-------------

subunitreporter is a plugin for Twisted Trial which adds a new reporter.
The reporter emits subunit v2 result streams with timing information.

Usage Sample
------------

Use this with your trial command-lines.
For example::

  $ trial --reporter=subunitv2 ... | subunit-stats

Installing
----------

To install the latest version of subunitreporter using pip::

  $ pip install subunitreporter

For additional development dependencies, install the ``dev`` extra::

  $ pip install subunitreporter[dev]

Testing
-------

subunitreporter uses pyunit-style tests.
After installing the development dependencies, you can run the test suite with trial::

  $ pip install subunitreporter[dev]
  $ trial subunitreporter

License
-------

subunitreporter is open source software released under the MIT License.
See the LICENSE file for more details.

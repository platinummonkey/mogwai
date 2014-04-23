.. _contribute:

Contributing
============

mogwai is distributed under the Apache 2.0 License.

Issues should be opened through `Bitbucket Issues <http://bitbucket.org/wellaware/mogwai/issues/>`_; whenever
possible, a pull request should be included.

All pull requests should pass the test suite, which can be launched simply with:

.. code-block:: sh

    $ make test

.. note::

    Running test requires `nosetests`, `coverage`, `six`, `pyformance` and `factory_boy`.

In order to test coverage, please use:

.. code-block:: sh

    $ pip install coverage
    $ coverage erase; make coverage
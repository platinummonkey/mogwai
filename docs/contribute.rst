.. _contribute:

Contributing
============

License
-------

``mogwai`` is distributed under the `Apache 2.0 License <http://www.apache.org/licenses/LICENSE-2.0.html>`_.


Issues
------

Issues should be opened through `Bitbucket Issues <http://bitbucket.org/wellaware/mogwai/issues/>`_; whenever
possible, a pull request should be included.


Pull Requests
-------------

All pull requests should pass the test suite, which can be launched simply with:

.. code-block:: sh

    $ make test

.. note::

    Running test requires `nosetests`, `coverage`, `six`, `pyformance`, `rexpro` and `factory_boy`. As well an available titan server.

In order to test coverage, please use:

.. code-block:: sh

    $ pip install coverage
    $ coverage erase; make coverage

Test Server
-----------

``mogwai`` was designed for `Titan <http://thinkaurelius.github.io/titan/>`_, other graph databases that utilize `Blueprints <https://github.com/tinkerpop/blueprints/wiki>`_
may be compatible, but further testing would be needed.

Currently Titan 0.4.2 is known to work and can be downloaded: `Titan <http://s3.thinkaurelius.com/downloads/titan/titan-server-0.4.2.zip>`_.

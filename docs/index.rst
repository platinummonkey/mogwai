mogwai
========

mogwai is an object graph mapper (OGM) designed for Titan Graph Database.

It's features include:

- Straightforward syntax
- Query Support
- Vertex and Edge Support
- Uses RexPro connection
- Supports Relationship quick-modeling
- Supports custom gremlin scripts and methods
- Doesn't restrict the developer from using direct methods.
- Save Strategies
- Property Validation
- Optionally can utilize `factory_boy <http://factoryboy.readthedocs.org/en/latest/>`_ to generate models.


Links
-----

* Documentation: http://mogwai.readthedocs.org/
* Official Repository: https://bitbucket.org/wellaware/mogwai.git
* Package: https://pypi.python.org/pypi/mogwai/

mogwai is known to support Python 2.7. Testing needs to be done on Python3 and PyPy.


Download
--------

PyPI: https://pypi.python.org/pypi/mogwai/

.. code-block:: sh

    $ pip install mogwai

Source: https://bitbucket.org/wellaware/mogwai.git

.. code-block:: sh

    $ git clone git://bitbucket.org/wellaware/mogwai.git
    $ python setup.py install


Usage
-----

.. note:: This section provides a quick summary of mogwai features.
           A more detailed listing is available in the full documentations.


Defining Models
"""""""""""""""

Models declare a Vertex or Edge model and attributes it should possibly contain.

.. code-block:: python

    from mogwai.models import Vertex, Edge

    def counter():
    global _val
    _val += 1
    return _val


    class TestVertexModel(Vertex):
        element_type = 'test_vertex_model'

        name = String(default='test_vertex')
        test_val = Integer(default=counter)


    class TestEdgeModel(Edge):
        label = 'test_edge_model'

        name = String(default='test_edge')
        test_val = Integer(default=counter)


Using Models
""""""""""""

mogwai models can be utilized in a similar fashion to the way the Django ORM was constructed... TODO


Contributing
------------

mogwai is distributed under the ???? License.

Issues should be opened through `Bitbucket Issues <http://bitbucket.org/wellaware/mogwai/issues/>`_; whenever
possible, a pull request should be included.

All pull requests should pass the test suite, whcih can be launched simply with:

.. code-block:: sh

    $ make test

.. note::

    Running test requires nosetests, six and factory_boy.

In order to test coverage, please use:

.. code-block:: sh

    $ pip install coverage
    $ coverage erase; make coverage


Contents
--------

.. toctree::
   :maxdepth: 2

   introduction
   internals
   reference
   recipes
   changelog
   ideas



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _example_migrations:

Migrations Example
==================

Here we illustrate the migrations of Vertex and Edge models

Original Models
---------------

.. literalinclude:: code/migrations_orig.py
    :language: python
    :linenos:


New Models
----------

.. literalinclude:: code/migrations_new.py
    :language: python
    :linenos:


Migration Result
----------------

Initial Setup Migration

.. literalinclude:: code/0001_migrations.py
    :language: python
    :linenos:

Actual Migration of models

.. literalinclude:: code/0002_migrations.py
    :language: python
    :linenos:

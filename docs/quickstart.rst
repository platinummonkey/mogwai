.. _quickstart:

Quick Start
===========

Usage
-----

.. note:: This section provides a quick summary of mogwai features.
           A more detailed listing is available in the full documentation.


.. _quickstart_setup_connection:

Setup Connection
----------------

You'll need to setup the connection to the graph database.  Mogwai handles connection pooling for you, but you
should handle load balancing using dedicated equipment.

.. code-block:: python

   from mogwai.connection import setup

   # Without Authentication
   setup('localhost')
   # With authentication
   #setup('localhost', username='rexster', password='rexster')
   # With gevent support
   #setup('localhost', concurrency='gevent')  # default is Standard Synchronous Python Sockets
   # With eventlet support
   #setup('localhost', concurrency='eventlet')  # default is Standard Synchronous Python Sockets

.. _quickstart_define_models:

Defining Models
---------------

Models declare a Vertex or Edge model and attributes it should possibly contain.

.. code-block:: python

   from mogwai.models import Vertex, Edge
   from mogwai.properties import String, Integer

   _val = 0

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


.. _quickstart_using_models:

Using Models
------------

mogwai models can be utilized in a similar fashion to the way the Django ORM was constructed, but tailored for Graph Databases.

Creating Vertex or Edge
"""""""""""""""""""""""

.. code-block:: python

   my_vertex_1 = TestVertexModel.create(name='my vertex')
   my_vertex_2 = TestVertexModel.create(name='my other vertex')
   my_edge = TestEdgeModel.create(outV=my_vertex_1, inV=my_vertex_2, name='my edge')


Retriveing a Vertex or Edge
"""""""""""""""""""""""""""

.. code-block:: python

   # Get all the TestVertexModel Vertices
   vertices = TestVertexModel.all()
   # Get a subset of vertices by titan ID
   vertices = TestVertexModel.all([1234, 5678, 9012])
   # Get a vertex by titan ID
   vertex = TestVertexModel.get(1234)

   # Getting all Edges isn't currently supported
   # Get a subset of edges by titan IDs
   edges = TestEdgeModel.all(['123-UX4', '215-PX3', '95U-32Z'])
   # get a single edge by titan ID
   edge = TestEdgeModel.get('123-UX4')

   # Get edge between two vertices
   edge = TestEdgeModel.get_between(outV=my_vertex_1, inV=my_vertex_2)


Simple Traversals
"""""""""""""""""

Vertex Traversals
'''''''''''''''''

.. code-block:: python

   # Get All Edges from the vertex
   edges = my_vertex_1.bothE()
   # Get outgoing edges from the vertex
   edges = my_vertex_1.outE()
   # Get incoming edges to the vertex
   edges = my_Vertex_1.inE()
   # Specify an edge type for any edge traversal operation (works for outE, inE, bothE)
   ## By using models
   test_model_edges = my_vertex_1.outE(TestEdgeModel)
   ## or by using manual labels
   test_model_edges = my_vertex_1.outE('test_edge_model')

   # Get all Vertices connected to the vertex
   vertices = my_vertex_1.bothV()
   # Get all vertices who are connected by edge coming into the current vertex (note uni-directed edges hide these, use bidirectional edges)
   vertices = my_vertex_1.outV()
   # Get all vertices who are connected by edge coming from the current vertex (note uni-directed edges hide these, use bidirectional edges)
   vertices = my_vertex_1.inV()
   # Specify an edge type for any edge traversal operation (works for outV, inV, bothV)
   ## By using models
   test_model_vertices = my_vertex_1.outV(TestEdgeModel)
   ## or by using manual element types
   test_model_vertices = my_vertex_1.outV('test_edge_model')


Edge Traversals
'''''''''''''''

.. code-block:: python

   # Get the vertex which is from the outgoing side of the edge
   vertex = my_edge.outV()
   # Get the vertex which is from the incoming side of the edge
   vertex = my_edge.inV()


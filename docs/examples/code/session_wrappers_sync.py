from mogwai import connection, properties
from mogwai.models import Vertex, Edge
from mogwai.tools import SessionPoolManager, BlueprintsWrapper, PartitionGraph
from mogwai.exceptions import MogwaiGremlinException

connection.setup('localhost')

##
#  Persist a session with SessionPoolManager
##

k = 10

with SessionPoolManager(bindings={'k': k}):
    gsk = connection.execute_query('"powers of ${k}"')
    pysk = "powers of {}".format(k)
    assert gsk == pysk

    kk = connection.execute_query("k * k")
    assert kk == k * k


##
#  Wrap the graph with a Blueprints Implementation
##

class BlueprintsWrapperVertex(Vertex):
    element_type = 'blueprints_wrapper_vertex'
    name = properties.String(required=True, max_length=128)


class BlueprintsWrapperEdge(Edge):
    element_type = 'blueprints_wrapper_edge'
    name = properties.String(required=True, max_length=128)

v0 = BlueprintsWrapperVertex.create(name="valid")

with BlueprintsWrapper(class_name='ReadOnlyGraph'):
    v0 = BlueprintsWrapperVertex.get(v0._id)
    try:
        BlueprintsWrapperVertex.create(name="illegal")
    except MogwaiGremlinException:
        print "java.lang.UnsupportedOperationException: \
               It is not possible to mutate a ReadOnlyGraph"


##
#  Treat the graph as a Partition Graph
##

with PartitionGraph(write='a'):
    v1 = BlueprintsWrapperVertex.create(name="only in a")
    v3 = BlueprintsWrapperVertex.create(name="started in a")

with PartitionGraph(write='b', read=['a']):
    v2 = BlueprintsWrapperVertex.create(name="only in b")
    e1 = BlueprintsWrapperEdge.create(outV=v2, inV=v1, name="only in b")
    v3.name = "still in a"
    v3.save()

with PartitionGraph(write='a'):
    v1 = BlueprintsWrapperVertex.get(v1._id)
    assert len(v1.bothE()) == 0
    try:
        BlueprintsWrapperVertex.get(v2._id)
    except BlueprintsWrapperVertex.DoesNotExist:
        print "vertex is located in partition B"

# outside of the session all the elements are accessible
print v1.bothE()[0]
# BlueprintsWrapperEdge(label=blueprints_wra..., values={'name': 'only in b'})

print dict(BlueprintsWrapperVertex.get(v3._id))
# {'_partition': 'a', 'name': 'still in a'}
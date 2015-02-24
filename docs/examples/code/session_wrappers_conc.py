from mogwai import connection, properties
from mogwai.models import Vertex, Edge
from mogwai.tools import SessionPoolManager, PartitionGraph
import eventlet

connection.setup('localhost', concurrency='eventlet')

##
#  Persist a session with SessionPoolManager
##

def isolation_test(scope):
    wrapper_config = {
        'bindings': {'scope': scope},
        'pool_size': 5
    }
    scope_values = []

    with SessionPoolManager(**wrapper_config) as pool:
        for i in range(7):
            scope_val = connection.execute_query(
                "scope *= 2",
                isolate=False,
                pool=pool
            )
            scope_values.append(scope_val)

    return scope, scope_values

pile = eventlet.GreenPile()
[pile.spawn(isolation_test, i) for i in range(10)]

for scope, scope_values in pile:
    assert scope_values == [scope * 2**i for i in range(1, 8)]


##
#  Treat the graph as a Partition Graph
##

class BlueprintsWrapperVertex(Vertex):
    element_type = 'blueprints_wrapper_vertex'
    name = properties.String(required=True, max_length=128)


class BlueprintsWrapperEdge(Edge):
    element_type = 'blueprints_wrapper_edge'
    name = properties.String(required=True, max_length=128)

n = 5

with PartitionGraph(write='a') as pool:
    av_pile = eventlet.GreenPile()
    for i in range(n):
        av_pile.spawn(BlueprintsWrapperVertex.create, name="only in a", pool=pool)
    vertices_in_a = list(av_pile)

with PartitionGraph(write='b', read=['a']) as pool:
    bv_pile = eventlet.GreenPile()
    for i in range(n):
        bv_pile.spawn(BlueprintsWrapperVertex.create, name="only in b", pool=pool)

    [pile.spawn(isolation_test, i) for i in range(n)]

    be_pile = eventlet.GreenPile()
    for vb in bv_pile:
        va = vertices_in_a.pop()
        scope, scope_values = pile.next()
        va[str(scope)] = scope_values
        av_pile.spawn(va.save, pool=pool)

        be_pile.spawn(BlueprintsWrapperEdge.create, outV=vb, inV=va,
                      name="only in b", pool=pool)

    vertices_in_a = [av for av in av_pile]
    edges_in_b = [be for be in be_pile]

for v in BlueprintsWrapperVertex.all():
    print v._id, dict(v), v.outE()

[pile.spawn(v.delete) for v in BlueprintsWrapperVertex.all()]
list(pile)


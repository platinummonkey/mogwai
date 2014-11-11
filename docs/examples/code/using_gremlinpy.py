from mogwai.connection import setup, execute_query
from mogwai.models.element import Element
from mogwai import properties
from mogwai import gremlin
from mogwai.models import Vertex, Edge
from functools import partial
import datetime
from pytz import utc
from gremlinpy.gremlin import Gremlin as GlobalQuery

setup('127.0.0.1')


class IsFriendsWith(Edge):
    label = 'is_friends_with'

    since = properties.DateTime(required=True,
                                default=partial(datetime.datetime.now, tz=utc),
                                description='Friends with since')


class Person(Vertex):

    element_type = 'person'  # this is optional, will default to the class name
    gremlin_path = 'custom_gremlin.groovy'

    name = properties.String(required=True, max_length=512)
    email = properties.Email(required=True)

    friends_and_friends_of_friends = gremlin.GremlinMethod(method_name='friends_and_friends_of_friends',
                                                           property=True,
                                                           defaults={'friend_edge_label': IsFriendsWith.get_label()})

    @property
    def friends(self):
        return self.bothV(IsFriendsWith)

    @property
    def out_vertices(self):
        g = GlobalQuery()
        return global_query_deserialize(g.v(bob.id).outE(IsFriendsWith.get_label()).inV)


bob = Person.create(name='Bob', email='bob@bob.net')
alice = Person.create(name='Alice', email='alice@alice.net')
IsFriendsWith.create(outV=bob, inV=alice)


def global_query_deserialize(global_query):
    """

    :param global_query: GlobalQuery
    :return: object | None
    """
    params = global_query.bound_params
    script = str(global_query)
    return Element.deserialize(execute_query(script, params))

g = GlobalQuery()
query = g.V('element_type', Person.element_type).outE(IsFriendsWith.label).inV

results = global_query_deserialize(query)
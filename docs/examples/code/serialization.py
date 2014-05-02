from mogwai.connection import setup
from mogwai.models import Vertex, Edge
from mogwai import properties
from mogwai import relationships
from mogwai._compat import print_
import datetime
from pytz import utc
from functools import partial
import pickle


setup('127.0.0.1')


class OwnsObject(Edge):

    label = 'owns_object'  # this is optional, will default to the class name

    since = properties.DateTime(required=True,
                                default=partial(datetime.datetime.now, tz=utc),
                                description='Owned object since')


class Trinket(Vertex):

    element_type = 'gadget'

    name = properties.String(required=True, max_length=1024)


class Person(Vertex):

    element_type = 'person'  # this is optional, will default to the class name

    name = properties.String(required=True, max_length=512)
    email = properties.Email(required=True)

    # Define a shortcut relationship method
    belongings = relationships.Relationship(OwnsObject, Trinket)


## Creation
# Create a trinket
trinket = Trinket.create(name='Clock')

# Create a Person
bob = Person.create(name='Bob Smith', email='bob@bob.net')

# Create the Ownership Relationship
relationship = OwnsObject.create(outV=bob, inV=trinket)


bob_serialized = pickle.dumps(bob)
print_("Bob Serialized: {}".format(bob_serialized))
deserialized_bob = pickle.loads(bob_serialized)
print_("Bob Deserialized: {}".format(deserialized_bob))
assert bob == bob_serialized

relationship_serialized = pickle.dumps(relationship)
print_("Relationship Serialized: {}".format(relationship_serialized))
deserialized_relationship = pickle.loads(relationship_serialized)
print_("Relationship Deserialized: {}".format(deserialized_relationship))
assert relationship == relationship_serialized


trinket_serialized = pickle.dumps(trinket)
print_("Trinket Serialized: {}".format(trinket_serialized))
deserialized_trinket = pickle.loads(trinket_serialized)
print_("Trinket Deserialized: {}".format(deserialized_trinket))
assert trinket == trinket_serialized
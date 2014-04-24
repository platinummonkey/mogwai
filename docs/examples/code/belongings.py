from mogwai.connection import setup
from mogwai.models import Vertex, Edge
from mogwai import properties
from mogwai import relationships
from mogwai._compat import print_
import datetime
from pytz import utc
from functools import partial


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


## Traversals
# Find out what bob owns
bob_owns_relationships = bob.belongings.vertices()
bob_owns_vertex_traversal = bob.outV(OwnsObject)

print_("With Relationships: Bob owns: {}".format(bob_owns_relationships))

# Another method for the same thing
print_("With Vertex Traversal: Bob owns: {}".format(bob_owns_vertex_traversal))
assert bob_owns_relationships == bob_owns_vertex_traversal


# Find out who owns the trinket
print_("With Vertex Traversal: Trinket is owned by: {}".format(trinket.inV(OwnsObject)))

# When was the trinket owned?
print_("Trinket has been owned since: {}".format(relationship.since))
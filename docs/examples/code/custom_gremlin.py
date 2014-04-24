from mogwai.connection import setup
from mogwai.models import Vertex, Edge
from mogwai import properties
from mogwai import gremlin
from mogwai._compat import print_
import datetime
from pytz import utc
from functools import partial

setup('127.0.0.1')


class IsFriendsWith(Edge):
    label = 'is_friends_with'

    since = properties.DateTime(required=True,
                                default=partial(datetime.datetime.now, tz=utc),
                                description='Owned object since')


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


## Creation
# Create the People
bob = Person.create(name='Bob', email='bob@bob.net')
alice = Person.create(name='Alice', email='alice@alice.net')
john = Person.create(name='John', email='john@john.net')
tim = Person.create(name='Tim', email='tim@tim.net')
kyle = Person.create(name='Kyle', email='kyle@kyle.net')

# Create Friendships
IsFriendsWith.create(outV=bob, inV=alice)
IsFriendsWith.create(outV=alice, inV=john)
IsFriendsWith.create(outV=alice, inV=tim)
IsFriendsWith.create(outV=tim, inV=kyle)

## Traverse
# All known direct friends with Bob
bobs_friends = bob.friends
print_("Bobs direct friends: {}".format(bobs_friends))
# Output:
# [ Person(element_type=person, id=8132, values={'name': Alice, 'email': alice@alice.net}) ]


# Friends and Friends of Friends using Custom Gremlin Method
bobs_friends_and_friends_of_friends = bob.friends_and_friends_of_friends
print_("Bobs Friends and Friends of Friends: {}".format(bobs_friends_and_friends_of_friends))

# Output:
# [
#   [ Person(element_type=person, id=8128, values={'name': Bob, 'email': bob@bob.net}),
#     Person(element_type=person, id=8132, values={'name': Alice, 'email': alice@alice.net}),
#     Person(element_type=person, id=8136, values={'name': John, 'email': john@john.net})
#    ], [
#     Person(element_type=person, id=8128, values={'name': Bob, 'email': bob@bob.net}),
#     Person(element_type=person, id=8132, values={'name': Alice, 'email': alice@alice.net}),
#     Person(element_type=person, id=8140, values={'name': Tim, 'email': tim@tim.net})
#    ]
# ]

for friend_set in bobs_friends_and_friends_of_friends:
    assert len(friend_set) <= 3
    assert friend_set[0] == bob
    assert friend_set[1] == alice
    assert kyle not in friend_set
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


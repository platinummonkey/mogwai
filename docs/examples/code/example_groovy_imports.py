from mogwai.connection import setup
from mogwai.models import Vertex
from mogwai import properties
from mogwai.gremlin import GremlinMethod

setup('127.0.0.1')


class Trinket(Vertex):

    element_type = 'gadget'

    name = properties.String(required=True, max_length=1024)

    test_method = GremlinMethod(path='example_groovy_imports.groovy', method_name='test_method',
                                imports=['com.thinkaurelius.titan.core.util.*'], classmethod=True)

# Call the test method:
result1, result2 = Trinket.test_method(1, 2)
assert result1 == 1
assert result2 == 2
from mogwai.connection import setup
from mogwai.models import Vertex
from mogwai import properties

setup('127.0.0.1')


class Trinket(Vertex):

    element_type = 'gadget'

    name = properties.String(required=True, max_length=1024)


## Creation
# Create a trinket
# create with un-modeled property
trinket = Trinket.create(name='Clock', engraving='Bob Smith')
assert trinket['engraving'] == 'Bob Smith'

# get with un-modeled property
result = Trinket.get(trinket.id)
assert result['engraving'] == 'Bob Smith'

# change property from trinket (and persist to database)
trinket['engraving'] = 'Alice Smith'
assert trinket['engraving'] == 'Alice Smith'
trinket.save()
assert trinket['engraving'] == 'Alice Smith'

# delete property from trinke (and persist to database)
del trinket['engraving']
try:
    result = trinket['engraving']
    raise Exception("Property shouldn't exist")
except AttributeError:
    pass
trinket.save()
try:
    result = trinket['engraving']
    raise Exception("Property shouldn't exist")
except AttributeError:
    pass

# iterate through keys
keys = [key for key in trinket]
keys = [key for key in trinket.keys()]
values = [value for value in trinket.values()]
items = [item for item in trinket.items()]
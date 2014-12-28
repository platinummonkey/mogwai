

class BaseIndexSpecification(object):
    """ Base Mogwai Index Specification used for Elements, properties and composite indices """

    def __init__(self, index_key=None, index_ext=None, *args, **kwargs):
        self._index_key = index_key
        self.index_ext = index_ext

    @property
    def index_key(self):
        return self._index_key

    def _set_index_key_name(self, index_key):
        self._index_key = index_key

    def get_specification(self):
        return vars(self)

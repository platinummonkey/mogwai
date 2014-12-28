from mogwai.exceptions import MogwaiMigrationException


def get_loaded_models():
    from mogwai.connection import _loaded_models
    return [model for model in _loaded_models
            if (not model.__abstract__ and model.__name__ not in ('Element', 'Vertex', 'Edge'))]


def _ask_for_it_by_name(name):
    """ Returns an object referenced by absolute path.

    :param name: string reference to import
    :return: mogwai.models.element.Element | mogwai.models.properties.base.GraphProperty
    """
    bits = str(name).split(".")

    ## what if there is no absolute reference?
    if len(bits) > 1:
        modulename = ".".join(bits[:-1])
    else:
        modulename = bits[0]

    module = __import__(modulename, {}, {}, bits[-1])

    if len(bits) == 1:
        return module
    else:
        return getattr(module, bits[-1])


def ask_for_it_by_name(name):
    """ Returns an object referenced by absolute path. (Memoised outer wrapper)

    :param name: string reference to import
    :return: mogwai.models.element.Element | mogwai.models.properties.base.GraphProperty
    """
    if name not in ask_for_it_by_name.cache:
        ask_for_it_by_name.cache[name] = _ask_for_it_by_name(name)
    return ask_for_it_by_name.cache[name]
ask_for_it_by_name.cache = {}


class BaseMigration(object):

    def gf(self, model_name, property_name):
        """ Gets a property by absolute reference
        :param property_name: Property by absolute reference
        :type property_name: basestring
        :return: mogwai.properties.base.GraphProperty
        """
        prop = ask_for_it_by_name(property_name)
        return prop


class SchemaMigration(BaseMigration):
    pass

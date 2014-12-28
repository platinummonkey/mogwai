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


def value_clean(model, property):
    """

    :param model: mogwai.models.element.Element
    :param property: mogwai.properties.base.GraphProperty
    :return: Return quadruple representing state of the model property
    :rtype: None | tuple(mogwai.models.element.Element, mogwai.properties.base.GraphProperty,
                         object|None, callable | None)
    """

    if model.__abstract__:
        return None
    if property.default is None and property.required:
        raise MogwaiMigrationException("Required Value specified and no default specified: {} -> {}".format(
            model, property.db_field_name))
    if property.default is not None:
        if callable(property.default):
            value = None
            func = property.default
        else:
            value = property.default
            func = None
        return model, property, value, func
    else:
        return model, property, None, None


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


class DataMigration(BaseMigration):
    """ Data Migrations shouldn't be dry-run """
    no_dry_run = True
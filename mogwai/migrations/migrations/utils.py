from mogwai.exceptions import MogwaiMigrationException
from mogwai.tools import import_string, ImportStringError
from mogwai.connection import Configuration


def get_import_path_for_class(klass):
    return klass.__module__ + '.' + klass.__name__


def get_loaded_models():
    """ Get all loaded models

    :return: list of all loaded models
    :rtype: [Element]
    """
    return [model for model in Configuration._get_loaded_models()
            if (not model.__abstract__ and model.__name__ not in ('Element', 'Vertex', 'Edge'))]


def get_loaded_models_for_app(app):
    """ Only return loaded models that match a given app name

    ie. given:
        myapp
          models.py
            - MyVertex
        myotherapp
          models.py
            -MyOtherVertex

    assert get_loaded_models_for_app('myapp.models') == '[MyVertex]'

    :param app: application name
    :type app: basestring
    :return: list of loaded models matching app location
    :rtype: [Element]
    """
    all_models = get_loaded_models()
    return [model for model in all_models if '.'.join(model.__module__.split('.')[:-1]) == app]


def ask_for_it_by_name(name):
    """ Returns an object referenced by absolute path. (Memoised outer wrapper)

    :param name: string reference to import
    :return: mogwai.models.element.Element | mogwai.models.properties.base.GraphProperty
    """
    if name not in ask_for_it_by_name.cache:
        try:
            ask_for_it_by_name.cache[name] = import_string(name)
        except ImportStringError as e:
            raise MogwaiMigrationException(e.message)
    return ask_for_it_by_name.cache[name]
ask_for_it_by_name.cache = {}


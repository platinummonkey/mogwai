from mogwai.migrations.utils import get_loaded_models


def freeze_apps(models=None):
    """ Take the loaded list of models and returns a string of their frozen form

    :return: str
    """
    if not models:
        _loaded_models = get_loaded_models()
    else:
        _loaded_models = models

    frozen_models = set()

    # for all models iterate through and only add non-abstract models
    for model in _loaded_models:
        if hasattr(model, '__abstract__') and model.__abstract__:
            pass
        else:
            frozen_models.add(model)
    # Serialize
    model_defs = {}
    model_classes = {}
    for model in frozen_models:
        model_defs[model_key(model)] = prep_model_for_freeze(model)
        model_classes[model_key(model)] = model
    return model_defs


def model_key(model):
    """For a given model, return 'appname.modelname'.

    :param model: Model
    :type model: mogwai.models.element.Element
    :rtype: str
    """
    return "{}.{}".format(model.__module__, model.__name__)


def prep_model_for_freeze(model):
    """
    Takes a model and returns the ready-to-serialise dict (all you need
    to do is just pretty-print it).
    """
    properties = model._properties
    # Remove useless attributes (like 'choices')
    for name, prop in properties.items():
        properties[name] = prop
    return properties

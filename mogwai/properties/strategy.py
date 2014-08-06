from __future__ import unicode_literals
from mogwai.exceptions import SaveStrategyException


class Strategy(object):
    """ Saving strategies for mogwai. These are used to indicate when a property
    should be saved after the initial vertex/edge creation.
    """

    @classmethod
    def condition(cls, previous_value, value, has_changed=False, first_save=False, graph_property=None):
        """ Default save strategy condition

        :raises: NotImplementedError
        """
        raise NotImplementedError("No Save Strategy condition defined")

    def __repr__(self):
        return "%s" % self.__class__.__name__

    def __str__(self):
        return self.__repr__()


class SaveOnce(Strategy):
    """ Only save this value once. If it changes throw an exception. """

    @classmethod
    def condition(cls, previous_value, value, has_changed=False, first_save=False, graph_property=None):
        """ Always save this value if it has changed

        :raises: SaveStrategyException
        :rtype: bool
        """
        if not first_save:
            field_name = getattr(graph_property, 'field_db_name', None)
            raise SaveStrategyException("Attempt to change property '%s' with save strategy SAVE_ONCE" % (field_name))
        else:
            return True


class SaveOnChange(Strategy):
    """ Only save this value if it has changed. """

    @classmethod
    def condition(cls, previous_value, value, has_changed=False, first_save=False, graph_property=None):
        """ Always save this value if it has changed

        :rtype: bool
        """
        return has_changed


class SaveAlways(Strategy):
    """ Save this value every time the corresponding model is saved. """

    @classmethod
    def condition(cls, previous_value, value, has_changed=False, first_save=False, graph_property=None):
        """ Save this value every time the corresponding model is saved.

        :rtype: bool
        """
        return True


class SaveOnIncrease(Strategy):
    """ Save this value only if it is increasing """

    @classmethod
    def condition(cls, previous_value, value, has_changed=False, first_save=False, graph_property=None):
        """ Only save this value if it is increasing

        :rtype: bool
        """
        if previous_value is not None:
            return value > previous_value
        else:
            return True


class SaveOnDecrease(Strategy):
    """ Save this value only if it is decreasing """

    @classmethod
    def condition(cls, previous_value, value, has_changed=False, first_save=False, graph_property=None):
        """ Only save this value if it is decreasing

        :rtype: bool
        """
        if previous_value is not None:
            return value < previous_value
        else:
            return True
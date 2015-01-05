"""
Actions - things like 'a model was removed' or 'a property was changed'.
Each one has a class, which can take the action description and insert code
blocks into the forwards() and backwards() methods, in the right place.
"""

from __future__ import unicode_literals, print_function

from mogwai._compat import print_
from mogwai.models import Vertex, Edge
from mogwai.exceptions import MogwaiMigrationException
from mock_elements import MockEdge, MockVertex
from utils import get_import_path_for_class


class Action(object):
    """
    Generic base Action class. Contains utility methods for inserting into
    the forwards() and backwards() method lists.
    """

    prepend_forwards = False
    prepend_backwards = False

    def forwards_code(self):
        raise NotImplementedError  # pragma: no cover

    def backwards_code(self):
        raise NotImplementedError  # pragma: no cover

    def add_forwards(self, forwards):
        if self.prepend_forwards:
            forwards.insert(0, self.forwards_code())
        else:
            forwards.append(self.forwards_code())

    def add_backwards(self, backwards):
        if self.prepend_backwards:
            backwards.insert(0, self.backwards_code())
        else:
            backwards.append(self.backwards_code())

    def console_line(self):
        """Returns the string to print on the console, e.g. ' + Added field foo'"""
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def get_model_info(cls, model):
        try:
            if isinstance(model, MockVertex):
                return 'vertex', model.model_class_name, model.label
            elif isinstance(model, MockEdge):
                return 'edge', model.model_class_name, model.label
            elif issubclass(model, Vertex):
                return 'vertex', get_import_path_for_class(model), model.get_label()
            elif issubclass(model, Edge):
                return 'edge', get_import_path_for_class(model), model.get_label()
            else:
                raise MogwaiMigrationException("{} is Not a Vertex or Edge".format(model))
        except:
            raise MogwaiMigrationException("{} is Not a Vertex or Edge".format(model))


class AddElementType(Action):
    """
    Addition of an element type model. Takes the label for the element model subclass
    """

    FORWARDS_TEMPLATE = '''
        # Adding {model_type} '{model_class_name}'
        db.create_{model_type}_type('{label}')'''[1:] + "\n"

    BACKWARDS_TEMPLATE = '''
        # Deleting {model_type} '{model_class_name}'
        db.delete_{model_type}_type('{label}')'''[1:] + "\n"

    def __init__(self, model, package_name=''):
        self.package_name = package_name
        self.model = model
        self.model_type, self.model_class_name, self.label = Action.get_model_info(self.model)

    def console_line(self):
        """Returns the string to print on the console, e.g. ' + Added field foo'"""
        return " + Added element type {} for package {}".format(self.model_class_name, self.package_name)

    def forwards_code(self):
        """Produces the code snippet that gets put into forwards()"""

        return self.FORWARDS_TEMPLATE.format(
            model_type=self.model_type,
            model_class_name=self.model_class_name,
            label=self.label
        )

    def backwards_code(self):
        """Produces the code snippet that gets put into backwards()"""
        return self.BACKWARDS_TEMPLATE.format(
            model_class_name=self.model_class_name,
            label=self.label,
            model_type=self.model_type
        )


class DeleteElementType(AddElementType):
    """
    Deletion of an element type model. Takes the label for the element model subclass
    """

    def console_line(self):
        """Returns the string to print on the console, e.g. ' + Added field foo'"""
        return " - Deleted element type {} for package {}".format(self.model_class_name, self.package_name)

    def forwards_code(self):
        return AddElementType.backwards_code(self)

    def backwards_code(self):
        return AddElementType.forwards_code(self)


class AddProperty(Action):
    """
    Adds a property to an element model. Takes a Model class and the property.
    """

    FORWARDS_TEMPLATE = '''
        # Adding element property '{model_class_name}.{property_name}'
        db.create_property_key("{property_db_field}", data_type="{data_type}")'''[1:] + "\n"

    BACKWARDS_TEMPLATE = '''
        # Deleting element property '{model_class_name}.{property_name}'
        db.delete_property_key("{property_db_field}")'''[1:] + "\n"

    def __init__(self, model, prop, package_name=''):
        self.package_name = package_name
        self.model = model
        self.prop = prop
        self.prop_name = self.prop.property_name
        self.property_db_field = self.prop.db_field_name
        self.data_type = self.prop.data_type
        self.model_type, self.model_class_name, self.label = Action.get_model_info(self.model)

        # See if they've made property required but also have no default (far too common)
        is_required = self.prop.required
        default = self.prop.has_default

        if is_required and not default:
            print_("    * You've specified a property to be required but haven't specified a default value, you will\n"
                   "    * need to manually change the database to reflect the needed operations")
        elif is_required and default:
            print_("    * You've specified a property to be required and give a default value! Please note this will\n"
                   "    * not iterate over existing elements to include the new default value!")

    def console_line(self):
        """Returns the string to print on the console,

        e.g. ' + Added element property foo to mymodel for package mypackage'
        """
        return " + Added element property {} to {} for package {}".format(
            self.prop_name,
            self.model_class_name,
            self.package_name
        )

    def forwards_code(self):
        return self.FORWARDS_TEMPLATE.format(
            model_class_name=self.model_class_name,
            property_name=self.prop_name,
            property_db_field=self.property_db_field,
            data_type=self.data_type
        )

    def backwards_code(self):
        return self.BACKWARDS_TEMPLATE.format(
            model_class_name=self.model_class_name,
            property_name=self.prop_name,
            property_db_field=self.property_db_field
        )


class DeleteProperty(AddProperty):
    """
    Removes property to an element model. Takes a Model class and the property.
    """

    def console_line(self):
        """Returns the string to print on the console, e.g. ' + Added field foo'"""
        return " - Deleted element property {} to {} for package {}".format(
            self.prop_name,
            self.model_class_name,
            self.package_name
        )

    def forwards_code(self):
        return AddProperty.backwards_code(self)

    def backwards_code(self):
        return AddProperty.forwards_code(self)


class AddCompositeIndex(Action):
    """
    Adds an index to a model field[s]. Takes a Model class and the field names.
    """

    FORWARDS_TEMPLATE = '''
        # Adding composite index '{index_name}' for '{model_class_name}'
        db.create_composite_index("{index_key}", "{edge_key}", "{model_type}", indexer="{indexer}", composite_index={composite_index})'''[1:] + "\n"

    BACKWARDS_TEMPLATE = '''
        # Removing composite index '{index_name}' for '{model_class_name}'
        db.delete_composite_index("{index_key}", "{edge_key}", "{composite_index}")'''[1:] + "\n"

    prepend_backwards = True  # We need to delete composite indexes before any other major changes

    def __init__(self, model, index, package_name=''):
        self.package_name = package_name
        self.model = model
        self.index = index
        self.index_name = ''
        self.index_key = ''
        self.edge_key = ''
        self.model_type, self.model_class_name, self.label = Action.get_model_info(self.model)

    def console_line(self):
        """Returns the string to print on the console, e.g. ' + Added field foo'"""
        return " + Added index {} for model {} for package {}".format(
            self.index,
            self.model_class_name,
            self.package_name
        )

    def forwards_code(self):

        return self.FORWARDS_TEMPLATE.format(
            model_class_name=self.model_class_name,
            index_name=self.index_name,
            index_key=self.index_key,
            edge_key=self.edge_key,
            composite_index=self.index,
            model_type=self.model_type
        )

    def backwards_code(self):
        return self.BACKWARDS_TEMPLATE.format(
            model_class_name=self.model_class_name,
            index_name=self.index_name,
            index_key=self.index_key,
            edge_key=self.edge_key,
            composite_index=self.index
        )


class DeleteCompositeIndex(AddCompositeIndex):
    """
    Deletes an index off a model field[s]. Takes a Model class and the field names.
    """

    def console_line(self):
        """Returns the string to print on the console, e.g. ' + Added field foo'"""
        return " + Deleted index {} for model {} for package {}".format(
            self.index,
            self.model_class_name,
            self.package_name
        )

    def forwards_code(self):
        return AddCompositeIndex.backwards_code(self)

    def backwards_code(self):
        return AddCompositeIndex.forwards_code(self)

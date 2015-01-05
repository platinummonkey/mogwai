from __future__ import unicode_literals
from mock_elements import MockVertex, MockEdge


class MigrationChanges(object):

    def __init__(self, additions, deletions, changes, current, model):
        self.additions = additions
        self.deletions = deletions
        self.changes = changes
        self.current = current
        self.model = model

    def __repr__(self):
        return "{}(additions={}, deletions={}, changes={}, current={}, model={})".format(
            self.__class__.__name__, self.additions, self.deletions, self.changes, self.current, self.model
        )

    @property
    def null(self):
        return self.additions in (None, {}) and self.deletions in (None, {}) and self.changes in (None, {})


class MigrationCalculation(object):
    """ Calculate differences between states """

    @classmethod
    def to_migration(cls, previous_state, current_state):
        """ Calculate the total migration for the given models

        :param previous_state: Previous state of migration
        :type previous_state: mogwai.models.element.Element | MockVertex | MockEdge
        :param current_state: Current state state before migration
        :type current_state: mogwai.models.element.Element | MockVertex | MockEdge
        :return: migration changes
        :rtype [MigrationChanges]
        """
        return (MigrationCalculation.element_label_migrations(previous_state, current_state),
                MigrationCalculation.composite_indices_migrations(previous_state, current_state),
                MigrationCalculation.property_migrations(previous_state, current_state))

    @classmethod
    def element_label_migrations(cls, previous_state, current_state):
        if previous_state.get_label() != current_state.get_label():
            return MigrationChanges(current_state, previous_state, None, current_state, current_state)
        else:
            return MigrationChanges(None, None, None, current_state, current_state)

    @classmethod
    def composite_indices_migrations(cls, previous_state, current_state):
        return MigrationChanges(None, None, None, current_state.composite_indices, current_state)

    @classmethod
    def property_migrations(cls, previous_element, current_element):
        """ Calculate the changes for all the properties for the given element

        :param previous_element: previous element
        :type previous_element: mogwai.models.vertex.Vertex | mogwai.models.edge.Edge
        :param current_element: current element
        :type current_element: mogwai.models.vertex.Vertex | mogwai.models.edge.Edge
        :return: migration changes
        :rtype: MigrationChanges
        """
        if previous_element is None:
            return MigrationChanges(current_element._properties, None, None, current_element._properties, current_element)

        previous_properties = previous_element._properties
        """ :type previous_properties: dict """
        current_properties = current_element._properties
        """ :type current_properties: dict """

        additions, deletions, changed_properties = MigrationCalculation.dict_diff(previous_properties,
                                                                                  current_properties)

        # Additions
        for k, v in additions.items():
            additions[k] = v._definition()

        # Deletions
        for k, v in deletions.items():
            deletions[k] = v._definition()

        # Changes
        changes = {}
        for k, v in changed_properties.items():
            migration = MigrationCalculation.property_migration(v[0], v[1], current_element)
            if not migration.null:
                if k not in changes:
                    changes[k] = []
                changes[k].append(migration)
        return MigrationChanges(additions, deletions, changes, current_element._properties, current_element)

    @classmethod
    def property_migration(cls, previous_state, current_state, current_element):
        """ Calculate the differences between two property states

        :param previous_state: previous property state
        :type previous_state: mogwai.properties.base.GraphProperty
        :param current_state: current property state
        :type current_state: mogwai.properties.base.GraphProperty
        :return: additions, deletions, changes, current_state
        :rtype: [dict]
        """

        prev_dict = previous_state._definition()
        cur_dict = current_state._definition()
        added, removed, changed = MigrationCalculation.dict_diff(prev_dict, cur_dict)

        return MigrationChanges(added, removed, changed, current_state, current_element)

    @classmethod
    def dict_diff(cls, prev_dict, cur_dict):
        """ Compares two dictionaries and evalates the additions, deletions and changes for all key-value pairs

        :param prev_dict: previous dictionary
        :type prev_dict: dict
        :param cur_dict: current dictionary
        :type cur_dict: dict
        :return: changesets
        :rtype: [dict]
        """
        set_prev = set(prev_dict.keys())
        set_cur = set(cur_dict.keys())
        intersect = set_cur.intersection(set_prev)

        added = set_cur - intersect
        removed = set_prev - intersect
        changed = set(p for p in intersect if p != 'default' and prev_dict[p] != cur_dict[p])

        added_dict = dict([(k, cur_dict[k]) for k in added])
        removed_dict = dict([(k, prev_dict[k]) for k in removed])
        changed_dict = dict([(k, (prev_dict[k], cur_dict[k])) for k in changed])

        return added_dict, removed_dict, changed_dict


class ActionCalculations(object):

    @classmethod
    def to_actions(cls, element_label_changes, composite_indices_changes, properties_changes):
        """ Convert MigrationChanges to Actions that have forward and backward code generation methods

        :param element_label_changes: element label migration changes
        :type element_label_changes: MigrationChanges
        :param composite_indices_changes: composite index migration changes
        :type composite_indices_changes: MigrationChanges
        :param properties_changes: element properties migration changes
        :type properties_changes: MigrationChanges
        :return: [actions.Action]
        """
        actions = []
        actions.extend(cls.element_label_changes(element_label_changes))
        actions.extend(cls.properties_changes(properties_changes))
        actions.extend(cls.composite_indices_changes(composite_indices_changes))
        return actions

    @classmethod
    def element_label_changes(cls, element_label_changes):
        """ Convert MigrationChanges to Actions that have forward and backward code generation methods

        :param element_label_changes: element label migration changes
        :type element_label_changes: [MigrationChanges]
        :return: [actions.Action]
        """
        actions = []
        return actions

    @classmethod
    def composite_indices_changes(cls, composite_indices_changes):
        """ Convert MigrationChanges to Actions that have forward and backward code generation methods

        :param composite_indices_changes: composite index migration changes
        :type composite_indices_changes: MigrationChanges
        :return: [actions.Action]
        """
        actions = []
        return actions

    @classmethod
    def properties_changes(cls, properties_changes):
        """ Convert MigrationChanges to Actions that have forward and backward code generation methods

        :param properties_changes: element properties migration changes
        :type properties_changes: MigrationChanges
        :return: [actions.Action]
        """
        actions = []
        return actions
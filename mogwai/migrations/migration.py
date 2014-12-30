from __future__ import unicode_literals, print_function

import sys
import datetime
from pytz import timezone, utc
from mogwai.properties import String, Text
from mogwai.models import Vertex, Edge
from mogwai.exceptions import MogwaiMigrationException
from models import MigrationRoot, Migration, PerformedMigration
from state import MigrationCalculation
from utils import get_loaded_models, ask_for_it_by_name
from actions import *


class DatabaseOperation(object):

    def __init__(self, alias, dry_run=False):
        self.alias = alias
        self.dry_run = dry_run

    # Create
    def create_vertex_type(self, state):
        pass

    def create_edge_type(self, state):
        pass

    def send_create_signal(self, etype, name):
        pass

    def create_property_key(self, state):
        pass

    def create_composite_index(self, state):
        pass

    # Delete
    def delete_vertex_type(self, state):
        pass

    def delete_edge_type(self, state):
        pass

    def send_delete_signal(self, etype, name):
        pass

    def delete_property_key(self, state):
        pass

    def delete_composite_index(self, state):
        pass

    def sync_indices(self):
        pass

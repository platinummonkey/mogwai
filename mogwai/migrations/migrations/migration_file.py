from __future__ import unicode_literals
import os


class AppMigrations(object):
    pass


class PreviousMigration(object):
    """ Class which represents a particular migration file on-disk. """

    def __init__(self, filename):
        self.filename = filename
        self.dependencies = set()
        self.dependents = set()

    def __repr__(self):
        return '{}(filename={}, dependencies={}, dependents={})'.format(
            self.__class__.__name__, self.filename, self.dependencies, self.dependents
        )

    @property
    def stripped_filename(self):
        return os.path.splitext(os.path.basename(self.filename))[0]
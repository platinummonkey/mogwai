from __future__ import unicode_literals
import os
import argparse


class BaseCommand(object):

    help = ''
    usage_str = ''

    parser = argparse.ArgumentParser()
    parser.add_argument('--dry_run', action='store_true', help='Do not perform migration, onlyl print out to STDOUT')

    def __init__(self, *args, **kwargs):
        self.current_directory = os.getcwd()
        self.args = None

    def setup_args(self):
        pass

    def parse_args(self):
        self.args = self.parser.parse_args()

    def get_file_path(self, klass):
        """ Get the file path of a class

        :param klass: reference class
        :type klass: object
        :return: directory of class
        :rtype: basestring
        """
        return os.dirname(klass.__file__)

    def get_migration_file_default_path(self, klass):
        """ Get the default migrations directory for the given class

        :param klass: reference class
        :type klass: object
        :return: directory of default migration storage
        :rtype: basestring
        """
        return os.path.join(self.get_file_path(klass), 'migrations')

    def handle(self, *args, **kwargs):
        raise NotImplementedError("Method must be overridden")

    def __call__(self, forwards=True, *args, **kwargs):
        self.parse_args()
        self.handle(**vars(self.args))

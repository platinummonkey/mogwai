from __future__ import unicode_literals
import os
import argparse


class BaseCommand(object):

    parser = argparse.ArgumentParser()
    help = ''
    usage_str = ''

    def __init__(self, *args, **kwargs):
        self.current_directory = os.getcwd()

    def setup_args(self):
        pass

    def parse_args(self):
        self.parser.parse_args()

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

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Call method must be overridden")

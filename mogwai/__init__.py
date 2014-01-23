import os

__mogwai_version_path__ = os.path.realpath(__file__ + '/../VERSION')
__version__ = open(__mogwai_version_path__, 'r').readline().strip()

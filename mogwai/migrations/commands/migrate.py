from __future__ import unicode_literals
import argparse
from base import BaseCommand


class MigrateCommand(BaseCommand):
    pass

if __name__ == '__main__':
    c = MigrateCommand()
    c()
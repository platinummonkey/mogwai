import sys

sys.path.append('.')

NUM_OBJECTS = 10

BROKER_URL = 'redis://localhost:6379/0'

CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

CELERY_IMPORTS = ('tasks', )

from celery import group, Celery
from celery.utils.log import get_task_logger
import os
import time
from mogwai._compat import print_
from mogwai.connection import setup
from mogwai.models import Vertex
from mogwai.properties import String

logger = get_task_logger(__name__)

setup(os.getenv('TITAN_HOST', 'localhost'), 'graph')

app = Celery('tasks')
app.config_from_object('celeryconfig')


class TestCeleryVertex(Vertex):

    name = String(default='test vertex', required=True)


@app.task(timeout=5, max_retries=1)
def test_query():
    results = TestCeleryVertex.all()
    assert len(results) > 0
    return results


@app.task(timeout=5, max_retries=1)
def test_delete(obj):
    """
    :type obj: Vertex
    """
    obj.delete()


@app.task(timeout=10, max_retries=1)
def test_retrieval(num_objects):
    for i in range(num_objects):
        TestCeleryVertex.create(name='test celery vertex {}'.format(i))
    time.sleep(2)
    g = group(test_query.s())
    results = g().join()
    lresults = len(results[0])
    print_("Got {} results of {}:".format(lresults, num_objects))
    for i, result in enumerate(results[0]):
        print_("{} - {}".format(i, result))
        logger.info("{} - {}".format(i, result))
    print_("Got {} of {} results ({}%):".format(lresults, num_objects, (lresults/float(num_objects))*100.0))
    g = group([test_delete.s(o) for o in results[0]])
    g().join()
    return results
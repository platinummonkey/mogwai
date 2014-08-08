from __future__ import unicode_literals
from mogwai._compat import integer_types
from nose.plugins.attrib import attr
from mogwai.tests.base import BaseMogwaiTestCase
from mogwai.metrics.base import get_time, BaseMetricsReporter, MetricsRegistry
from mogwai.exceptions import MogwaiMetricsException


@attr('unit', 'metrics')
class BaseMetricReporterTestCase(BaseMogwaiTestCase):
    """
    Test Base Metric Reporter
    """

    def test_time_method(self):
        import time
        self.assertAlmostEqual(get_time(), time.time(), 0)

    def test_default_construction(self):
        mr = BaseMetricsReporter()
        self.assertIsInstance(mr.registry, (tuple, list))
        self.assertEqual(len(mr.registry), 1)
        self.assertIsInstance(mr.registry[0], MetricsRegistry)

    def test_single_reporter_construction(self):
        r = MetricsRegistry()
        mr = BaseMetricsReporter(registry=r)
        self.assertIsInstance(mr.registry, (tuple, list))
        self.assertEqual(len(mr.registry), 1)
        self.assertIsInstance(mr.registry[0], MetricsRegistry)
        self.assertEqual(mr.registry[0], r)

    def test_multiple_reporter_constuction(self):
        r = [MetricsRegistry(), MetricsRegistry()]
        mr = BaseMetricsReporter(registry=r)
        self.assertIsInstance(mr.registry, (tuple, list))
        self.assertEqual(len(mr.registry), 2)
        self.assertIsInstance(mr.registry[0], MetricsRegistry)
        self.assertEqual(mr.registry, r)

    def test_bad_construction(self):

        class NotMetricReporter(object):
            pass

        r = [NotMetricReporter()]
        with self.assertRaises(MogwaiMetricsException):
            mr = BaseMetricsReporter(registry=r)

    def test_start_stop_mechanism(self):
        mr = BaseMetricsReporter()
        mr.start()
        self.assertTrue(mr.task.running)
        mr.stop()
        self.assertFalse(mr.task.running)

    def test_metric_getter(self):
        mr = BaseMetricsReporter()
        mr.start()
        # increment a counter
        mr.registry[0].counter('test').inc()
        timestamp, metrics = mr.get_metrics()
        self.assertIsInstance(timestamp, integer_types)
        self.assertIsInstance(metrics, dict)
        self.assertEqual(len(metrics), 1)
        self.assertIn('test', metrics)
        self.assertIsInstance(metrics['test'], dict)
        self.assertEqual(metrics['test']['count'], 1)
        mr.stop()

    def test_metric_sender(self):
        mr = BaseMetricsReporter()
        mr.start()
        mr.registry[0].counter('test').inc()
        mr.send_metrics()
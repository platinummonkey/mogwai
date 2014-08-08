from __future__ import unicode_literals
from mogwai._compat import integer_types, PY2, get_method_self
from nose.plugins.attrib import attr
from mogwai.metrics.manager import MetricManager
from mogwai.tests.base import BaseMogwaiTestCase
from mogwai.metrics.base import BaseMetricsReporter, MetricsRegistry
from mogwai.exceptions import MogwaiMetricsException


@attr('unit', 'metrics')
class MetricManagerTestCase(BaseMogwaiTestCase):
    """
    Test Metric Manager
    """

    def test_default_construction(self):
        mm = MetricManager()
        self.assertEqual(mm.metric_reporters, [])
        with self.assertRaises(MogwaiMetricsException):
            mm.setup_reporters(None)
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)

        self.assertIsInstance(mm.metric_reporters, (tuple, list))
        self.assertEqual(len(mm.metric_reporters), 1)
        self.assertIsInstance(mm.metric_reporters[0], BaseMetricsReporter)
        self.assertEqual(mm.metric_reporters, [mr])

    def test_multiple_reporter_constuction(self):
        mm = MetricManager()
        r1 = [MetricsRegistry(), MetricsRegistry()]
        mr1 = BaseMetricsReporter(registry=r1)
        r2 = [MetricsRegistry(), MetricsRegistry()]
        mr2 = BaseMetricsReporter(registry=r2)
        mm.setup_reporters([mr1, mr2])

        self.assertIsInstance(mm.metric_reporters, (tuple, list))
        self.assertEqual(len(mm.metric_reporters), 2)
        self.assertIsInstance(mm.metric_reporters[0], BaseMetricsReporter)
        self.assertIsInstance(mm.metric_reporters[1], BaseMetricsReporter)
        self.assertEqual(mm.metric_reporters, [mr1, mr2])

    def test_bad_construction(self):
        mm = MetricManager()

        class NotMetricReporter(object):
            pass

        mr = [NotMetricReporter()]
        with self.assertRaises(MogwaiMetricsException):
            mm.setup_reporters(mr)

    def test_start_stop_mechanism(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)
        mm.start()
        for mr in mm.metric_reporters:
            self.assertTrue(mr.task.running)
        mm.stop()
        for mr in mm.metric_reporters:
            self.assertFalse(mr.task.running)

    def test_metric_getter(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)
        mm.start()
        # increment counters
        for counter in mm.counters('test'):
            counter.inc()

        timestamp, metrics = mr.get_metrics()
        self.assertIsInstance(timestamp, integer_types)
        self.assertIsInstance(metrics, dict)
        self.assertEqual(len(metrics), 1)
        self.assertIn('test', metrics)
        self.assertIsInstance(metrics['test'], dict)
        self.assertEqual(metrics['test']['count'], 1)
        mm.stop()

    def test_counter_decorator(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)
        mm.start()

        @mm.count_calls
        def somefunc(i):
            return i

        @mm.count_calls
        def badfunc(i):
            raise Exception("test exception")

        self.assertEqual(somefunc(1), 1)
        self.assertEqual(somefunc(1, context='test'), 1)
        with self.assertRaises(Exception):
            badfunc(1)

        # check metrics collected
        for reporter in mm.metric_reporters:
            timestamp, metrics = reporter.get_metrics()
            self.assertIsInstance(timestamp, integer_types)
            self.assertIsInstance(metrics, dict)
            self.assertEqual(len(metrics), 5)

            # context aware
            self.assertIn('test.counter', metrics)
            self.assertIsInstance(metrics['test.counter'], dict)
            self.assertEqual(metrics['test.counter']['count'], 1)

            # normal one
            self.assertIn('somefunc.calls', metrics)
            self.assertIsInstance(metrics['somefunc.calls'], dict)
            self.assertEqual(metrics['somefunc.calls']['count'], 2)

        mm.stop()

    def test_timer_decorator(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)
        mm.start()

        @mm.time_calls
        def somefunc(i):
            return i

        @mm.time_calls
        def badfunc(i):
            raise Exception("test exception")

        self.assertEqual(somefunc(1), 1)
        self.assertEqual(somefunc(1, context='test'), 1)
        with self.assertRaises(Exception):
            badfunc(1)

        # check metrics collected
        for reporter in mm.metric_reporters:
            timestamp, metrics = reporter.get_metrics()

            self.assertIsInstance(timestamp, integer_types)
            self.assertIsInstance(metrics, dict)
            self.assertEqual(len(metrics), 5)

            # context aware
            self.assertIn('test.timer', metrics)
            self.assertIsInstance(metrics['test.timer'], dict)
            self.assertLess(metrics['test.timer']['max'], 0.01)

            # normal one
            self.assertIn('somefunc.timer', metrics)
            self.assertIsInstance(metrics['somefunc.timer'], dict)
            self.assertLess(metrics['somefunc.timer']['max'], 0.01)

        mm.stop()

    def test_meter_decorator(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)
        mm.start()

        @mm.meter_calls
        def somefunc(i):
            return i

        @mm.meter_calls
        def badfunc(i):
            raise Exception("test exception")

        self.assertEqual(somefunc(1), 1)
        self.assertEqual(somefunc(1, context='test'), 1)
        with self.assertRaises(Exception):
            badfunc(1)

        # check metrics collected
        for reporter in mm.metric_reporters:
            timestamp, metrics = reporter.get_metrics()
            self.assertIsInstance(timestamp, integer_types)
            self.assertIsInstance(metrics, dict)
            self.assertEqual(len(metrics), 5)

            # context aware
            self.assertIn('test.meter', metrics)
            self.assertIsInstance(metrics['test.meter'], dict)
            self.assertGreater(metrics['test.meter']['mean_rate'], 100)

            # normal one
            self.assertIn('somefunc.calls', metrics)
            self.assertIsInstance(metrics['somefunc.calls'], dict)
            self.assertGreater(metrics['somefunc.calls']['mean_rate'], 100)

        mm.stop()

    def test_histogram_decorator(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)
        mm.start()

        @mm.hist_calls
        def somefunc(i):
            return i

        @mm.hist_calls
        def badfunc(i):
            raise Exception("test exception")

        self.assertEqual(somefunc(1), 1)
        self.assertEqual(somefunc(1, context='test'), 1)
        with self.assertRaises(Exception):
            badfunc(1)

        # check metrics collected
        for reporter in mm.metric_reporters:
            timestamp, metrics = reporter.get_metrics()
            self.assertIsInstance(timestamp, integer_types)
            self.assertIsInstance(metrics, dict)
            self.assertEqual(len(metrics), 4)

            # context aware
            self.assertIn('test.hist', metrics)
            self.assertIsInstance(metrics['test.hist'], dict)
            self.assertEqual(metrics['test.hist']['count'], 1)

            # normal one
            self.assertIn('somefunc.calls', metrics)
            self.assertIsInstance(metrics['somefunc.calls'], dict)
            self.assertEqual(metrics['somefunc.calls']['count'], 2)

        mm.stop()

    def test_multiple_decorators(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)
        mm.start()

        @mm.meter_calls
        @mm.count_calls
        @mm.hist_calls
        @mm.time_calls
        def somefunc(i):
            return i

        self.assertEqual(somefunc(1), 1)
        self.assertEqual(somefunc(1, context='test'), 1)

        # check metrics collected
        for reporter in mm.metric_reporters:
            timestamp, metrics = reporter.get_metrics()
            self.assertIsInstance(timestamp, integer_types)
            self.assertIsInstance(metrics, dict)
            self.assertEqual(len(metrics), 3)

            # context aware
            self.assertIn('test.meter', metrics)
            self.assertIsInstance(metrics['test.meter'], dict)
            self.assertGreater(metrics['test.meter']['mean_rate'], 100)

            # normal one
            self.assertIn('somefunc.calls', metrics)
            self.assertIsInstance(metrics['somefunc.calls'], dict)
            self.assertEqual(metrics['somefunc.calls']['count'], 2)

        mm.stop()

    def test_get_all_timers(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)

        # test default implementation
        for timer in mm.timers():
            self.assertIsNotNone(get_method_self(timer))
            self.assertIsInstance(get_method_self(timer), MetricsRegistry)

        # test context aware
        for timer in mm.timers('test'):
            from pyformance.meters.timer import Timer
            self.assertIsInstance(timer, Timer)

    def test_get_all_histograms(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)

        # test default implementation
        for hist in mm.histograms():
            self.assertIsNotNone(get_method_self(hist))
            self.assertIsInstance(get_method_self(hist), MetricsRegistry)

        # test context aware
        for hist in mm.histograms('test'):
            from pyformance.meters.histogram import Histogram
            self.assertIsInstance(hist, Histogram)

    def test_get_all_meters(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)

        # test default implementation
        for meter in mm.meters():
            self.assertIsNotNone(get_method_self(meter))
            self.assertIsInstance(get_method_self(meter), MetricsRegistry)

        # test context aware
        for meter in mm.meters('test'):
            from pyformance.meters.meter import Meter
            self.assertIsInstance(meter, Meter)

    def test_get_all_counters(self):
        mm = MetricManager()
        mr = BaseMetricsReporter()
        mm.setup_reporters(mr)

        # test default implementation
        for counter in mm.counters():
            self.assertIsNotNone(get_method_self(counter))
            self.assertIsInstance(get_method_self(counter), MetricsRegistry)

        # test context aware
        for counter in mm.counters('test'):
            from pyformance.meters.counter import Counter
            self.assertIsInstance(counter, Counter)
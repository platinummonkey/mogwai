from __future__ import unicode_literals
from pyformance.registry import MetricsRegistry, RegexRegistry
import time
from twisted.internet import task
from mogwai.exceptions import MogwaiMetricsException
from mogwai._compat import print_


def get_time():
    return int(round(time.time()))


class BaseMetricsReporter(object):
    """ Base Metrics Reporter class

    Customize this class for the specific metrics service, ie. Graphite, NewRelic, etc.
    """

    def __init__(self, registry=None, reportingInterval=5*60, metric_prefix=None):
        """ Create a Metrics Reporter

        To override this method, please make sure to call the superclass *after* your methods. Ie.
        def __init__(self, mystuff, stuff2=None, *args, **kwargs):
            # do my stuff...
            super(MyClass, self).__init__(*args, **kwargs)

        :param registry: The pyformance registry
        :type registry: list[ MetricsRegistry | RegexRegistry ] | MetricsRegistry | RegexRegistry
        :param reportingInterval: The interval (number of seconds) on which to report the collected metrics.
        :type reportingInterval: float | long | int
        :param metric_prefix: The prefix on the collected metrics. The default implementation ignores this.
        :type metric_prefix: basestring | None
        """
        self.setup_registry(registry=registry)
        self.reporting_interval = reportingInterval
        self.metric_prefix = metric_prefix or ''
        self.task = None

    def start(self):
        """ Start the Metric Reporter """
        self.start_reporter(self.reporting_interval)

    def stop(self):
        """ Stop the Metric Reporter """
        self.task.stop()

    def setup_registry(self, registry=None):
        """ Setup the Metric Reporter with the given registry(s) """
        if not registry:
            self.registry = [MetricsRegistry(), ]
        else:
            if not isinstance(registry, (tuple, list)):
                registry = [registry, ]
            self.registry = []
            for reg in registry:
                if not isinstance(reg, (MetricsRegistry, RegexRegistry)):
                    raise MogwaiMetricsException(
                        "%s is not an instance of pyformance.MetricsRegistry or pyformance.RegexRegistry"
                    )
                self.registry.append(reg)

    def start_reporter(self, reportingInterval):
        """ Start the Metric Reporter Agent

        Kicks off a loop that every reportingInterval runs the `send_metrics` method.

        :param reportingInterval: The interval (number of seconds) on which to report the collected metrics.
        :type reportingInterval: float | long | int
        """
        self.task = task.LoopingCall(self.send_metrics)
        self.task.start(reportingInterval)

    def _get_metrics(self, timestamp=None, *args, **kwargs):
        """ Default pyformance implementation to collect all the metrics from the registries.

        Change only if you know what you are doing.

        :param timestamp: use this timestamp instead of the generated timestamp when the method is run
        :type timestamp: long | int
        :returns: Timestamp and aggregated metrics from all registries.
        :rtype: tuple( long | int, dict )
        """
        if not timestamp:
            timestamp = get_time()
        metrics = {}
        for reg in self.registry:
            metrics.update(reg.dump_metrics())
        return timestamp, metrics

    def get_metrics(self, timestamp=None, *args, **kwargs):
        """ Default pyformance implementation to collect all the metrics from the registries.

        Change this if you wan't customize for a particular metric collection system, ie. graphite, newrelic, etc.

        :param timestamp: use this timestamp instead of the generated timestamp when the method is run
        :type timestamp: long | int
        :returns: Timestamp and aggregated metrics from all registries.
        :rtype: tuple( long | int, dict )
        """
        return self._get_metrics(timestamp)

    def send_metrics(self, *args, **kwargs):
        """ Default pyformance implementation is to dump all metrics to STDOUT

        Change this if you want to customize for a particular metric collection system, ie. graphite, newrelic, etc.
        """
        timestamp, metrics = self.get_metrics()
        if metrics:
            print_("{}: {}".format(timestamp, metrics))


ConsoleMetricReporter = BaseMetricsReporter

__all__ = ['MetricsRegistry', 'RegexRegistry', 'Counter', 'Histogram', 'Meter', 'Timer', 'MogwaiMetricsException',
           'BaseMetricsReporter', 'ConsoleMetricReporter']

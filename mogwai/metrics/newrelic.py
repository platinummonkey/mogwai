from __future__ import unicode_literals
from mogwai._compat import print_
from mogwai.metrics.base import BaseMetricsReporter
import newrelic


class NewRelicReporter(BaseMetricsReporter):
    """ NewRelic Metrics Reporter class

    If you have a hosted newrelic service, you can log the OGM metrics to your newrelic service.
    """

    def __init__(self, config_file, environment=None, *args, **kwargs):
        """ Create a Metrics Reporter

        To override this method, please make sure to call the superclass *after* your methods. Ie.
        def __init__(self, mystuff, stuff2=None, *args, **kwargs):
            # do my stuff...
            super(MyClass, self).__init__(*args, **kwargs)

        :param config_file: The NewRelic Configuration File
        :type config_file: basestring
        :param environment: The NewRelic Configuration Environment (optional)
        :type environment: basestring
        :param metric_prefix: The prefix on the collected metrics. The default implementation ignores this.
        :type metric_prefix: basestring | None
        :param registry: The pyformance registry
        :type registry: list[ MetricsRegistry | RegexRegistry ] | MetricsRegistry | RegexRegistry
        :param reportingInterval: The interval (number of seconds) on which to report the collected metrics.
        :type reportingInterval: float | long | int
        """
        self.agent = newrelic.agent
        self.agent.initialize(config_file, environment=environment)
        super(NewRelicReporter, self).__init__(*args, **kwargs)

    def convert_metric_name(self, key, metric):
        """ Converts the mogwai naming schema to NewRelic naming schema

        :param key: the mogwai metric key
        :type key: basestring
        :param metric: the specific metric being collected
        :type key: basestring
        :returns: Converted key
        :rtype: basestring
        """
        return 'Custom/' + key.replace('.', '/') + '/' + metric

    def send_metrics(self):
        """ Default Hosted Graphite implementation is to dump all metrics to STDOUT

        Change this if you want to customize for a particular metric collection system, ie. graphite, newrelic, etc.
        """
        metrics = self.get_metrics()
        if not metrics:
            return

        for mkey, metric in metrics.items():
            for mname, mval in metric.items():
                try:
                    self.agent.record_custom_metric(self.convert_metric_name(mkey, mname), mval, None)
                except Exception as e:
                    print_(e)

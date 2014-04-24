from __future__ import unicode_literals
from mogwai._compat import print_, urllib
from mogwai.metrics.base import BaseMetricsReporter
import base64


class HostedGraphiteReporter(BaseMetricsReporter):
    """ Hosted Graphite Metrics Reporter class

    If you have a hosted graphite service, you can log the OGM metrics to your graphite service.
    """

    def __init__(self, api_key, url='https://hostedgraphite.com/api/v1/sink', *args, **kwargs):
        """ Create a Metrics Reporter

        To override this method, please make sure to call the superclass *after* your methods. Ie.
        def __init__(self, mystuff, stuff2=None, *args, **kwargs):
            # do my stuff...
            super(MyClass, self).__init__(*args, **kwargs)

        :param api_key: The Hosted Graphite API key
        :type api_key: basestring
        :param url: The Hosted Graphite API url
        :type url: basestring
        :param metric_prefix: The prefix on the collected metrics. The default implementation ignores this.
        :type metric_prefix: basestring | None
        :param registry: The pyformance registry
        :type registry: list[ MetricsRegistry | RegexRegistry ] | MetricsRegistry | RegexRegistry
        :param reportingInterval: The interval (number of seconds) on which to report the collected metrics.
        :type reportingInterval: float | long | int
        """
        self.url = url
        self.api_key = api_key
        super(HostedGraphiteReporter, self).__init__(*args, **kwargs)

    def send_metrics(self):
        """ Default Hosted Graphite implementation is to dump all metrics to STDOUT

        Change this if you want to customize for a particular metric collection system, ie. graphite, newrelic, etc.
        """
        metrics = self.get_metrics()
        if metrics:
            try:
                request = urllib.Request(self.url, metrics)
                request.add_header("Authorization", "Basic {}".format(base64.encodestring(self.api_key).strip()))
                result = urllib.urlopen(request)
            except Exception as e:
                print_(e)

    def get_metrics(self, timestamp=None):
        """ Default Hosted Graphite implementation to collect all the metrics from the registries and upload to a
        hosted graphite

        :param timestamp: use this timestamp instead of the generated timestamp when the method is run
        :type timestamp: long | int
        :returns: Timestamp and aggregated metrics from all registries.
        :rtype: tuple( long | int, dict )
        """
        timestamp, metrics = self._get_metrics(timestamp)
        metrics_data = []
        for key in metrics.keys():
            for valuekey in metrics[key].keys():
                metrics_data.append('{}_{}.{} {} {}\n'.format(self.metric_prefix,
                                                              key,
                                                              valuekey,
                                                              metrics[key][valuekey],
                                                              timestamp))
            return ''.join(metrics_data)

from mogwai._compat import print_
from .base import BaseMetricsReporter
from mogwai.exceptions import MogwaiMetricsException
from pyformance import call_too_long
import time
from functools import wraps
import logging


logger = logging.getLogger(__name__)


class TimerContext(object):
    """ Timer Context Manager customization to compensate for multiple Metric Registries """
    def __init__(self, timers, clock=time, *args, **kwargs):
        super(TimerContext, self).__init__()
        self.clock = clock
        self.timers = timers
        self.start_time = self.clock.time()
        self.kwargs = kwargs
        self.args = args

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = self.clock.time() - self.start_time
        for timer in self.timers:
            """ @type timer : pyformance.meters.timer.Timer """
            timer._update(elapsed)
            if timer.threshold and timer.threshold < elapsed:  # pragma: no cover
                # this is a future feature in pyformance and will need to be tested
                call_too_long.send(timer, elapsed=elapsed, *self.args, **self.kwargs)
        if exc_type is not None:
            return False
        return elapsed


class MetricManager(object):
    """ Manages your Metric Agents

    Properly inject mogwai metrics, while still allowing custom app metrics
    """

    def __init__(self):
        self.metric_reporters = []  #BaseMetricsReporter()]

    def setup_reporters(self, metric_reporters):
        """ Setup the Metric Reporter(s) for the MetricManager """
        if not metric_reporters:
            raise MogwaiMetricsException("No Metric Reporters provided!")
        if not isinstance(metric_reporters, (list, tuple)):
            metric_reporters = [metric_reporters, ]

        for mr in metric_reporters:
            if not isinstance(mr, BaseMetricsReporter):
                raise MogwaiMetricsException("{} Not derived from Mogwai BaseMetricsReporter".format(mr))

        self.metric_reporters = metric_reporters

    def start(self):
        """ Start the Metric Reporter """
        for mr in self.metric_reporters:
            mr.start()

    def stop(self):
        """ Stop the Metric Reporter """
        for mr in self.metric_reporters:
            mr.stop()

    def timers(self, key=None):
        """ Yield Metric Reporter Timers

        :param key: The metric key to use
        :type key: basestring
        """
        if not key:
            for mr in self.metric_reporters:
                for reg in mr.registry:
                    yield reg.timer
        else:
            for mr in self.metric_reporters:
                for reg in mr.registry:
                    yield reg.timer(key)

    def histograms(self, key=None):
        """ Yield Metric Reporter Histograms

        :param key: The metric key to use
        :type key: basestring
        """
        if not key:
            for mr in self.metric_reporters:
                for reg in mr.registry:
                    yield reg.histogram
        else:
            for mr in self.metric_reporters:
                for reg in mr.registry:
                    yield reg.histogram(key)

    def meters(self, key=None):
        """ Yield Metric Reporter Meters

        :param key: The metric key to use
        :type key: basestring
        """
        if not key:
            for mr in self.metric_reporters:
                for reg in mr.registry:
                    yield reg.meter
        else:
            for mr in self.metric_reporters:
                for reg in mr.registry:
                    yield reg.meter(key)

    def counters(self, key=None):
        """ Yield Metric Reporter Counters

        :param key: The metric key to use
        :type key: basestring
        """
        if not key:
            for mr in self.metric_reporters:
                for reg in mr.registry:
                    yield reg.counter
        else:
            for mr in self.metric_reporters:
                for reg in mr.registry:
                    yield reg.counter(key)

    def time_calls(self, fn):
        """
        Decorator to time the execution of the function.

        :param fn: the function to be decorated
        :type fn: C{func}
        :return: the decorated function
        :rtype: C{func}
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            fn_name = "{}.timer".format(fn.__name__)
            if 'context' in kwargs:
                context_name = "{}.timer".format(kwargs.get('context'))
                del kwargs['context']
                timers = [reg.timer(context_name) for mr in self.metric_reporters for reg in mr.registry]
            else:
                timers = []
            timers += [reg.timer(fn_name) for mr in self.metric_reporters for reg in mr.registry]
            with TimerContext(timers):
                try:
                    return fn(*args, **kwargs)
                except:
                    for mr in self.metric_reporters:
                        for reg in mr.registry:
                            reg.meter("mogwai.error.meter").mark()
                            reg.counter("mogwai.error").inc()
                    raise
        return wrapper

    def hist_calls(self, fn):
        """
        Decorator to check the distribution of return values of a function.

        :param fn: the function to be decorated
        :type fn: C{func}
        :return: the decorated function
        :rtype: C{func}
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            fn_name = "{}.calls".format(fn.__name__)
            context_name = None
            if 'context' in kwargs:
                context_name = "{}.hist".format(kwargs.get('context'))
                del kwargs['context']

            try:
                rtn = fn(*args, **kwargs)
                if isinstance(rtn, (int, float)):
                    for mr in self.metric_reporters:
                        for reg in mr.registry:
                            reg.histogram(fn_name).add(rtn)
                            if context_name:
                                reg.histogram(context_name).add(rtn)
                return rtn
            except:
                for mr in self.metric_reporters:
                    for reg in mr.registry:
                        reg.meter("mogwai.error.meter").mark()
                        reg.counter("mogwai.error").inc()
                raise
        return wrapper

    def meter_calls(self, fn):
        """
        Decorator to the rate at which a function is called.

        :param fn: the function to be decorated
        :type fn: C{func}
        :return: the decorated function
        :rtype: C{func}
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            fn_name = "{}.calls".format(fn.__name__)
            context_name = None
            if 'context' in kwargs:
                context_name = "{}.meter".format(kwargs.get('context'))
                del kwargs['context']

            for mr in self.metric_reporters:
                for reg in mr.registry:
                    reg.meter(fn_name).mark()
                    if context_name:
                        reg.meter(context_name).mark()
            try:
                return fn(*args, **kwargs)
            except:
                for mr in self.metric_reporters:
                    for reg in mr.registry:
                        reg.meter("mogwai.error.meter").mark()
                        reg.counter("mogwai.error").inc()
                raise
        return wrapper

    def count_calls(self, fn):
        """
        Decorator to track the number of times a function is called.

        :param fn: the function to be decorated
        :type fn: C{func}
        :return: the decorated function
        :rtype: C{func}
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            fn_name = "{}.calls".format(fn.__name__)
            context_name = None
            if 'context' in kwargs:
                context_name = "{}.counter".format(kwargs.get('context'))
                del kwargs['context']

            for mr in self.metric_reporters:
                for reg in mr.registry:
                    reg.counter(fn_name).inc()
                    if context_name:
                        reg.counter(context_name).inc()
            #print_("Trying function: %s" % fn_name)
            try:
                return fn(*args, **kwargs)
            except:
                for mr in self.metric_reporters:
                    for reg in mr.registry:
                        reg.meter("mogwai.error.meter").mark()
                        reg.counter("mogwai.error").inc()
                raise
        return wrapper

__all__ = ['MetricManager', 'MogwaiMetricsException']

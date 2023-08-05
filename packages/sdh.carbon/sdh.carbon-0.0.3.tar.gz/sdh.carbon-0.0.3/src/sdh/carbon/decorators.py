import time
import functools

from .stream import send_time


class measure(object):
    def __init__(self, prefix=None, name=None):
        self.prefix = None
        self.name = None

        if hasattr(prefix, '__call__'):
            self.func = prefix
            functools.update_wrapper(self, prefix)
        else:
            self.prefix = prefix
            self.name = name

    def __get__(self, obj, type=None):
        return functools.partial(self, obj)

    def __call__(self, *args, **kwargs):
        if not hasattr(self, 'func'):
            self.func = args[0]
            return functools.update_wrapper(self, self.func)

        metric = self.name or ('%s.%s' % (self.func.__module__,
                                          self.func.__name__))
        if self.prefix:
            metric = '%s.%s' % (self.prefix, metric)
        start = time.time()
        result = self.func(*args, **kwargs)
        duration = (time.time() - start) * 1000  # msec
        send_time(metric, duration)
        return result


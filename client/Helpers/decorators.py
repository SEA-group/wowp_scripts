# Embedded file name: scripts/client/Helpers/decorators.py


class CachedProperty(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls = None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result
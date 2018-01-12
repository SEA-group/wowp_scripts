# Embedded file name: scripts/client/Helpers/deprecatedUtils.py
from debug_utils import LOG_DEBUG

class DeprecatedObject(object):

    def __init__(self, name):
        self.__dict__['name'] = name
        self.__dict__['props'] = {}

    def __call__(self, *args, **kwargs):
        LOG_DEBUG('Deprecated %s is called' % self.name)

    def __getattr__(self, name):
        prop = self.props.get(name, None)
        if prop is None:
            propName = self.name + '.' + name
            prop = DeprecatedObject(propName)
            self.props[name] = prop
        return prop

    def __delattr__(self, name):
        LOG_DEBUG('Deprecated %s.%s is deleted' % (self.name, name))

    def __setattr__(self, name, value):
        LOG_DEBUG('Deprecated %s.%s is set to %r' % (self.name, name, value))

    def __repr__(self):
        LOG_DEBUG('DeprecatedObject %s' % self.name)
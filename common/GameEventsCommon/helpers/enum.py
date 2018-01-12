# Embedded file name: scripts/common/GameEventsCommon/helpers/enum.py


class DictLikeMembers(type):

    def __getitem__(cls, item):
        """Emulate dict behavior on class members"""
        return getattr(cls, item)


class Enum(object):
    """Enumeration const helper class"""
    __metaclass__ = DictLikeMembers
    _excluded = ()

    @classmethod
    def fromStringKeys(cls, **params):
        return {cls[key]:value for key, value in params.iteritems()}

    @classmethod
    def keys(cls):
        """Return all keys defined in const"""
        return (key for key, value in cls.items())

    @classmethod
    def items(cls):
        """Return (key, value) pairs defined in const"""
        return ((key, value) for key, value in cls.__dict__.iteritems() if not key.startswith('_') and key not in cls._excluded and key not in ('fromStringKeys', 'items', 'keys'))
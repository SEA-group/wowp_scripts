# Embedded file name: scripts/common/BWUserTypesCommon/FixedDictWrapper.py


class FixedDictWrapper(object):
    """Base class for all custom user types based on FixedDict type.
    More details at:
    https://confluence.wargaming.net/display/BWT152/Properties#Properties-ImplementingCustomPropertyDataTypes  
    """

    def __init__(self, fixedDict):
        self._fixedDict = fixedDict

    @property
    def fixedDict(self):
        return self._fixedDict


class FDMemberProxy(object):
    """Data descriptor for FixedDict proxy properties, 
    have to be used only with FixedDictWrapper instances.
    More details at:
    https://confluence.wargaming.net/display/BWT152/Properties#Properties-ImplementingCustomPropertyDataTypes
    """

    def __init__(self, name):
        self._name = name

    def __get__(self, instance, owner = None):
        if not instance:
            return self
        return instance.fixedDict[self._name]

    def __set__(self, instance, value):
        instance.fixedDict[self._name] = value
# Embedded file name: scripts/common/db/DBModel/DBModelBase.py
import copy
from DBProperty import DBPropertyBase, DBModelProperty

class DBModelMeta(type):

    def __new__(mcs, name, bases, attrs):
        properties = {}
        for pname, value in attrs.iteritems():
            if isinstance(value, DBPropertyBase):
                value.name = pname
                properties[pname] = value

        modelAttributes = attrs.setdefault('_MODEL_PROPERTIES', {})
        for base in reversed(bases):
            modelAttributes.update(getattr(base, '_MODEL_PROPERTIES', {}))

        modelAttributes.update(properties)
        return super(DBModelMeta, mcs).__new__(mcs, name, bases, attrs)


class DBModelBase(object):
    __metaclass__ = DBModelMeta
    _MODEL_PROPERTIES = {}

    def __init__(self):
        self._loadedFromDB = False
        self._modelPropertyValues = {name:p.default for name, p in self._MODEL_PROPERTIES.iteritems()}

    @property
    def loadedFromDB(self):
        return self._loadedFromDB

    def getPropertyValue(self, name):
        raise name in self._MODEL_PROPERTIES or AssertionError("Wrong property '{0}'".format(name))
        return self._modelPropertyValues[name]

    def setPropertyValue(self, name, value):
        raise name in self._MODEL_PROPERTIES or AssertionError("Wrong property '{0}'".format(name))
        self._modelPropertyValues[name] = value

    def copyTo(self, model):
        for name, prop in self._MODEL_PROPERTIES.iteritems():
            if isinstance(prop, DBModelProperty):
                sourceModel = prop.get(self)
                targetModel = prop.get(model)
                sourceModel.copyTo(targetModel)
            else:
                copiedValue = copy.deepcopy(prop.get(self))
                prop.set(model, copiedValue)

    def read(self, section):
        if section:
            self._loadedFromDB = True
            for name, prop in self._MODEL_PROPERTIES.iteritems():
                prop.read(section, instance=self)